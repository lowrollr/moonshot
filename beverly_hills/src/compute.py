
import pickle
import os
import importlib
import inspect
from time import sleep
from threading import Lock
import numpy as np
from indicators.indicator import Indicator

class ComputeEngine:
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
        self.indicators = []
        self.model = mod_obj['model']
        self.last_updated = 0
        self.ready = False
        self.windowSize = 15000
        self.createIndicators()
        

    def createIndicators(self):
        temp_indicators = []
        for ind in self.indicator_dict:
            indicatorClass = importIndicator(self.indicator_dict[ind]['type'])
            temp_indicators.append(indicatorClass(
                params=self.indicator_dict[ind]['params'],
                name=ind,
                scalingWindowSize=self.windowSize,
                value=self.indicator_dict[ind]['value']))

        # order indicators so that indicators that depend on other indicators are comptued last
        base_values = {'open', 'high', 'low', 'close', 'volume', 'trades'}
        names_so_far = set()
        while len(temp_indicators) > len(self.indicators):
            found_any = False
            for ind in temp_indicators:
                if ind not in self.indicators:
                    if ind.value in base_values or ind.value in names_so_far:
                        names_so_far.add(ind.name)
                        self.indicators.append(ind)
                        found_any = True
            if not found_any:
                print('Error importing indicators!')

    def prepare(self, newData):
        first_coin = self.coins[0]
        
        with self.lock:
            for coin in self.coins:
                self.data[coin] = dict()
                for ind in self.indicators:
                    self.data[coin].update(ind.compute(newData[coin]))
            self.last_updated = newData[first_coin]['time']
            if not self.ready:
                ready = True
                for f in self.features:
                    if f not in self.data[first_coin]:
                        ready = False
                        break

                self.ready = ready


    def predict(self, coin, time):
        while True:
            if self.last_updated == time:
                with self.lock:
                    if not self.ready:
                        return False
                    model_input = []
                    for f in self.features:
                        model_input.append(self.data[f])
                    model_input = np.array(model_input)
                    if self.probability_threshold:
                        return self.probability_threshold <= self.model.predict_proba(model_input)
                    else:
                        return 1 == self.model.predict(model_input)
            elif self.last_updated > time:
                print('Warning: trying to fetch old predictions, this should never happen')
                break
            else:
                sleep(0.01)
        return False

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

def importIndicator(name):
    module = importlib.import_module(f'indicators.{name.lower()}')
    for mod in dir(module):
        obj = getattr(module, mod)
        if inspect.isclass(obj) and issubclass(obj, Indicator) and obj != Indicator:
            return obj

    return None
    
    