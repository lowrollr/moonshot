'''
FILE: strategy.py
AUTHORS:
    -> Jacob Marshall (marshingjay@gmail.com)
WHAT:
    -> This file contains the Strategy superclass
'''
import os
import pickle
import multiprocessing as mp
from itertools import chain, repeat
import numpy as np
import tensorflow as tf
'''
CLASS: Strategy
WHAT:
    -> Implements a given order execution strategy
TODO:
    -> Maybe entry/exit functions should return Floats corresponding to confidence? (How would this impact the rest of our 
        infrastructure?)
'''
class Strategy:

    '''
    ARGS:
        -> None
    RETURN:
        -> None
    WHAT: 
        -> default __init__ implementation
        -> Nothing to see here, every subclass will have its own implementation of this
        -> Each subclass should instantiate and populate its list of Indicators so that they may be added to the dataset
            before the strategy is executed
    TODO:
        -> do check at the end for the indicators that are the same and remove
    '''
    def __init__(self, entry_models=[], exit_models=[]):
        self.entry_models = dict()
        self.exit_models = dict()
        self.indicators = []
        model_num = 1
        for name, version in entry_models:
            
            self.importModel(name, version, model_num, True)
            model_num += 1

        model_num = 1
        for name, version in exit_models:
            self.importModel(name, version, model_num, False)
            model_num += 1
        
        self.algo_indicators = []
        self.name = self.__class__.__name__

    '''
    ARGS:
        -> model (string): name of model. Corresponding directory name in the saved_models dir
        -> version (string): version number corresponding to modelin saved_models dir
    RETURN:
        -> ret_model, full_path (model object, string): model object to predict with 
        -> indicators (list[Indicator]): return the list of indicator objects
    WHAT: 
        -> This import the model and returns the model object and model path name
    TODO:
        -> add availibility for neural networks which are directories
    '''
    def importModel(self, model, version="latest", model_num=1, is_entry=True):
        #get the correct model
        base_dir = './v2/strategy/saved_models/' + model + '/'

        if version == 'latest': # fetch the latest version of the given strategy
            all_files = os.listdir(base_dir)
            highest_version = [0, 0]

            for f in [x for x in os.scandir(f'{base_dir}/')if x.is_dir()]:
                parts = f.name.split('_')
                version = int(parts[0])
                subversion = int(parts[1])
                if version == highest_version[0]:
                    if subversion > highest_version[1]:
                        highest_version = [version, subversion]
                elif version > highest_version[0]:
                    highest_version = [version, subversion]
                    
            # set version to be the highest version found
            version = f'{highest_version[0]}_{highest_version[1]}'
        
        # this code attempts to find the module (strategy) with the given name, 
        # and gets the corresponding object if it exists
        full_path = base_dir + version + '/' + model + '_' + version + '.sav'
        
        model_data = pickle.load(open(full_path, 'rb'))
        self.indicators.extend(model_data['indicators'])
        if is_entry:
            self.entry_models[model_num] = dict()
            self.entry_models[model_num]['features'] = list(model_data['features'])
            self.entry_models[model_num]['proba_threshold'] = model_data['proba_threshold']
            self.entry_models[model_num]['path'] = full_path
            if not model_data['model']: #this is a neural network
                pass
            else:
                self.entry_models[model_num]['model'] = model_data['model']
        else:
            self.exit_models[model_num] = dict()
            self.exit_models[model_num]['features'] = list(model_data['features'])
            self.exit_models[model_num]['proba_threshold'] = model_data['proba_threshold']
            self.exit_models[model_num]['path'] = full_path
            if not model_data['model']: #this is a neural network
                pass
            else:
                self.exit_models[model_num]['model'] = model_data['model']

        ret_model = model_data["model"]
        indicators = model_data["indicators"]
        #features (string)
        #proba_threshold (bool)

        return (ret_model, full_path), indicators


    '''
    ARGS:
        -> dataset (pandas Dataframe): dataset for this strategy
        -> numProcesses (int): number of processes to spin up
    RETURN:
        -> N/A
    WHAT: 
        -> This function is the wrapper for completing pre-processing for each of the models that we have in the strat
    '''
    def preProcessing(self, dataset, n_process):
        for k in list(self.entry_models.keys()):
            self.entry_models[k]['results'] = self.preProcessingHelper(self.entry_models[k]['path'], dataset, n_process)
        for k in list(self.exit_models.keys()):
            self.exit_models[k]['results'] = self.preProcessingHelper(self.exit_models[k]['path'], dataset, n_process)

    '''
    ARGS:
        -> model_path (string): string to the path of the file
        -> dataset (pandas Dataframe): dataset to test over in the multiprocessing
        -> numProcesses (int): how many processes to spawn, should correspond with processors availible
    RETURN:
        -> N/A
    WHAT: 
        -> Driving function for creating the process pool and then executing the model prediction there
    '''
    def preProcessingHelper(self, model_path, dataset, numProcesses):
    
        return self.modelProcess(dataset, model_path)

    '''
    ARGS:
        -> data (pandas Dataframe): part of the dataframe to create predictions
        -> model_path (pandas Dataframe): path where model is stored to then instantiate and perform prediction
    RETURN:
        -> the predictions from the model
    WHAT: 
        -> function called by each created process for creating the predictions
    '''
    def modelProcess(self, data, model_path):
        model_obj = pickle.load(open(model_path, 'rb'))
        if not model_obj["model"]:
            model_path = "/".join(model_path.split("/")[:-1])
            model = tf.keras.models.load_model(model_path)
            model_obj["is_nn"] = True
        else:
            model = model_obj["model"]
            model_obj["is_nn"] = False

        model_predictions = dict()

        if model_obj["proba_threshold"]:
            ret = np.array([])
            if model_obj["is_nn"]:
                ret = model.predict(data[model_obj['features']])[:,1]
            else:
                ret = model.predict_proba(data[model_obj['features']])[:,1]
            
            def filter_proba(prediction):
                if model_obj["proba_threshold"] < prediction:
                    return 1.0
                return 0.0
            predictions = list(map(filter_proba, ret))
            times = list(data['time'].values)
            for i, p in enumerate(predictions):
                model_predictions[times[i]] = p
            
            
        else:
            predictions = list(model.predict(data[model_obj['features']]))
            times = list(data['time'].values)
            for i, p in enumerate(predictions):
                model_predictions[times[i]] = p
        return model_predictions

    '''
    ARGS:
        -> data (Tuple): a single row from a dataframe
    RETURN:
        -> None
    WHAT: 
        -> this will be called every tick by the backtesting model
        -> put things in here that you want to happen every tick
            or want to keep track of between ticks
    '''
    def process(self, data):
        pass


    '''
    ARGS:
        -> None
    RETURN:
        -> self.indicators ([Indicator]): Strategy object's list of Indicator objects
    WHAT: 
        -> returns the Strategy's list of indicators
    '''
    def getIndicators(self):
        return self.indicators


    '''
    ARGS:
        -> data (Tuple): a single row from a dataframe
    RETURN:
        -> (Boolean): Whether or not to enter a position
    WHAT: 
        -> given the current data row, determine whether or not to enter a position
    '''  
    def calc_entry(self, data):
        return False


    '''
    ARGS:
        -> data (Tuple): a single row from a dataframe
    RETURN:
        -> (Boolean): Whether or not to exit a position
    WHAT: 
        -> given the current data row, determine whether or not to exit a position
    '''  
    def calc_exit(self, data):
        return False
