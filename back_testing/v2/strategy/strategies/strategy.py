'''
FILE: strategy.py
AUTHORS:
    -> Jacob Marshall (marshingjay@gmail.com)
WHAT:
    -> This file contains the Strategy superclass
'''
import os
import pickle

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
        full_path = base_dir + '/' + version + '/' + model + '_' + version + '.sav'
        
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
