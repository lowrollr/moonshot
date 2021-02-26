'''
FILE: compute.py
AUTHORS:
    -> Jacob Marshall (marshingjay@gmail.com)
WHAT:
    -> This file contains functionality that implements the following:
        -> Per tick computation for indicators and model output
        -> Importing models, indicators, and features
'''

import pickle
import os
import importlib
import inspect
from time import sleep
from threading import Lock
import numpy as np
from indicators.indicator import Indicator


'''
CLASS: ComputeEngine
WHAT:
    -> Implements tick by tick computing of indicators and model predictions
    -> Maps coins to sets of indicators with data & results queues
'''
class ComputeEngine:
    '''
    ARGS:
        -> coins ([String]): list of coins that we'll be trading
    RETURN:
        -> None
    WHAT: 
        -> Initializes the ComputEngine mechanics, such as threading lock, indicators, and features
        -> self.data & self.indicators are dicts mapping coins to data values and indicator objects
        -> imports model used to make predictions
        -> Initializes indicator objects as specified by model
    '''
    def __init__(self, coins):
        self.lock = Lock()
        self.data = dict()
        self.coins = coins
        for coin in self.coins:
            self.data[coin] = dict()
        mod_obj = importModel('strawmaker')
        self.features = mod_obj['features']
        self.probability_threshold = mod_obj['proba_threshold']
        self.indicator_dict = mod_obj['indicators']
        self.indicators = dict()
        for coin in self.coins:
            self.indicators[coin] = []
        self.model = mod_obj['model']
        self.last_updated = 0
        self.windowSize = 15000
        self.minUnstablePeriod = 200
        print(self.features, self.indicator_dict)
        self.createIndicators()
        
        
    '''
    ARGS:
        -> None
    RETURN:
        -> None
    WHAT: 
        -> Populates self.indicators dict with lists of instantiated indicator objects for each coin in self.coins
        -> orders indicators by dependancy (so indicators that don't depend on values from other indicators are calculated first)
    '''
    def createIndicators(self):
        base_values = {'open', 'high', 'low', 'close', 'volume', 'trades', 'time'}
        for coin in self.coins:
            temp_indicators = []
            for ind in self.indicator_dict:
                indicatorClass = importIndicator(self.indicator_dict[ind]['type'])
                temp_indicators.append(indicatorClass(
                    params=self.indicator_dict[ind]['params'],
                    name=ind,
                    scalingWindowSize=self.windowSize,
                    unstablePeriod=self.minUnstablePeriod,
                    value=self.indicator_dict[ind]['value']))

            # order indicators so that indicators that depend on other indicators are comptued last
            
            names_so_far = set()
            # this is mega inefficient
            while len(temp_indicators) > len(self.indicators[coin]):
                found_any = False
                for ind in temp_indicators:
                    if ind not in self.indicators[coin]:
                        if ind.value in base_values or ind.value in names_so_far:
                            names_so_far.add(ind.name)
                            self.indicators[coin].append(ind)
                            found_any = True
                if not found_any:
                    print('Error importing indicators!')
    '''
    ARGS:
        -> newData ({string: {string: float}}): single tick of new data, maps coin to dict of OHCLVT data
    RETURN:
        -> None
    WHAT: 
        -> computes indicators for each coin with the new tick of data
    '''
    def prepare(self, newData):
        first_coin = self.coins[0]
        with self.lock:
            for coin in self.coins:
                self.data[coin] = dict()
                for ind in self.indicators[coin]:
                    self.data[coin].update(ind.compute(newData[coin]))
            self.last_updated = newData[first_coin]['time']


    def allDataPrepare(self, newData):
        for coin in newData:
            for candle in newData[coin]:
                for ind in self.indicators[coin]:
                    ind.compute(candle)

    '''
    ARGS:
        -> coin (string): coin to generate a prediction for
        -> time (int): unix timestamp that prediction is needed for (for syncing purposes)
    RETURN:
        -> (bool): whether or not the model predicted a signal
    WHAT: 
        -> returns the model's prediction for a specified coin at a given timestamp (this should always be the current time)
        -> ensures that needed features are present in ComputeEngine's current data prior to making a prediction
        -> makes sure that data is ready for the given timestamp (it's possible it could still be being computed in another thread)
    '''
    def predict(self, coin, time):
        
        while True:
            if self.last_updated == time:
                with self.lock:
                    print(f'Data Cols: {self.data[coin].keys()}')
                    model_input = []
                    for f in self.features:
                        if f not in self.data[coin]:
                            print('Not all features present, cannot predict!')
                            return False
                        model_input.append(self.data[coin][f])
                    print(f'Model Input: {model_input}')
                    model_input = np.array(model_input).reshape(1, -1)
                    if self.probability_threshold:
                        return self.probability_threshold <= self.model.predict_proba(model_input)[0][1]
                    else:
                        return 1 == self.model.predict(model_input)[0][1]
            elif self.last_updated > time:
                print('Warning: trying to fetch old predictions, this should never happen')
                break
            else:
                sleep(0.01)
        return False
'''
ARGS:
    -> mod_name (string): model name to import
    -> version (string): model version to import (specifying 'latest' will grab the latest version)
RETURN:
    -> ({string: value}): dict with model information
WHAT: 
    -> unpickles model object and loads features needed (ordered), indicator specification, model type, and the model itself
    -> loads the specified name and version
'''
def importModel(mod_name, version="latest"):
    #get the correct model
    base_dir = f'saved_models/{mod_name}/'
    version_str = version
    if version == "latest":
        # all_files = os.listdir(base_dir)
        highest_version = [0, 0]

        for f in [x for x in os.scandir(f'{base_dir}/')if x.is_dir()]:
            parts = f.name.split('_')
            version_str = int(parts[0])
            subversion = int(parts[1])
            if version_str == highest_version[0]:
                if subversion > highest_version[1]:
                    highest_version = [version_str, subversion]
            elif version_str > highest_version[0]:
                highest_version = [version_str, subversion]
            
    # set version to be the highest version found
    version_str = f'{highest_version[0]}_{highest_version[1]}'

    full_path = base_dir + version_str + '/' + mod_name + '_' + version_str + '.sav'
    mod_obj = pickle.load(open(full_path, 'rb'))

    return mod_obj

'''
ARGS:
    -> name (string): name of indicator to import
RETURN:
    -> obj (Indicator object): Uninstantiated indicator object with the specified name
WHAT: 
    -> finds the given indicator by name if it exists in a module, returns an uninstantiated object
'''
def importIndicator(name):
    module = importlib.import_module(f'indicators.{name.lower()}')
    for mod in dir(module):
        obj = getattr(module, mod)
        if inspect.isclass(obj) and issubclass(obj, Indicator) and obj != Indicator:
            return obj

    return None
    
    