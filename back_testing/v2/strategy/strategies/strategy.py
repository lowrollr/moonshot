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
        self.entry_models = []
        self.exit_models = []
        self.entry_model_results = []
        self.exit_model_results = []

        self.indicators = []

        for name, version in entry_models:
            model, indicators = self.importModel(name, version)
            self.entry_models.append(model)
            self.indicators.extend(indicators)
        for name, version in exit_models:
            model, indicators = self.importModel(name, version)
            self.exit_models.append(model)
            self.indicators.extend(indicators)
        
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
    def importModel(self, model, version="latest"):
        #get the correct model
        base_dir = './v2/strategy/saved_models/' + model + '/'

        if version == 'latest': # fetch the latest version of the given strategy
            all_files = os.listdir(base_dir)
            highest_version = 0.0
            # find the highest version number
            for my_file in all_files:
                if my_file[:len(model)] == model:
                    my_version = my_file.split('_v')[1]
                    my_version = float(my_version.replace('_', '.'))
                    highest_version = max(my_version, highest_version)
                    
            # set version to be the highest version found
            version = str(highest_version).replace('.', '_')
        
        # this code attempts to find the module (strategy) with the given name, 
        # and gets the corresponding object if it exists
        full_path = base_dir + model + '_v' + version + "/" + model + '_v' + version + ".sav"
        
        model_data = pickle.load(full_path)

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
    def preProcessing(self, dataset, numProcesses=-1):
        for _, path in self.entry_models:
            self.entry_model_results.append(self.preProcessingHelper(path, dataset, numProcesses))
        for _, path in self.exit_models:
            self.exit_model_results.append(self.preProcessingHelper(path, dataset, numProcesses))

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
    def preProcessingHelper(self, model_path, dataset, numProcesses=-1):
        #get number of processors 
        processes = numProcesses
        if processes == -1:
            processes = mp.cpu_count()
        #initialize process pool
        process_pool = mp.Pool(processes)

        #split data
        N = int(len(dataset)/processes)
        frames = [ dataset.iloc[i*processes:(i+1)*processes].copy() for i in range(N) ]

        params = zip(frames, repeat(model_path))
        results = process_pool.starmap(self.modelProcess, params)

        return chain.from_iterable(results)


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
        model_obj = pickle.load(model_path)
        model = model_obj["model"]

        model_predictions = []

        if model_obj["predict_proba"]:
            ret = model.predict_proba(data)[:,1]
            
            def filter_proba(prediction):
                if model_obj["threshold"] < prediction:
                    return 1.0
                return 0.0

            model_predictions = list(map(filter_proba, ret))
            
        else:
            model_predictions = model.predict(data)

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
