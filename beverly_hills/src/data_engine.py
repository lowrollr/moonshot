import os
import pickle
from collections import deque

class DataEngine():
    def __init__(self, coins):
        self.model = None
        self.proba_thresh = 0.0
        self.max_period = 0
        self.features = dict()
        self.data_count = 0
        self.data_queue = dict()

        self.importModel("CLASSIFICATION_CHANGE_THIS")
        queueNames = self.initQueues()

        standardColumns = ['open', 'high', 'low', 'close', 'volume']

        max_period = max([queueNames[x] for x in queueNames])

        for coin in coins:
            self.data_queue[coin] = dict()
            for name in queueNames:
                self.data_queue[coin][name] = deque(maxlen=int(queueNames[name]))
            for col in standardColumns:
                if not col in queueNames:
                    self.data_queue[coin][col] = deque(maxlen=int(max_period))

    def initQueues(self):
        queueNames = dict()
        for feat in self.features:
            defaultVals = feat.split("$")
            if len(defaultVals) > 1:
                #do some default stuff to check periods
                pass
            else:
                for columnKey in self.features[feat]:
                    if 'period' in self.features[feat][columnKey]:
                        max_p = max(self.features[feat][columnKey]['period'])
                        if columnKey in queueNames:
                            queueNames[columnKey] = max(max_p, queueNames[columnKey])
                        else:
                            queueNames[columnKey] = max_p
        return queueNames
            

    '''
    ASSUMPTIONS:
        -> this is loading one model
        -> that model is a buy model
    '''
    def importModel(self, mod_name, version="latest"):
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

        self.features = mod_obj['features']
        self.model = mod_obj['model']
        self.proba_thresh = mod_obj['proba_threshold']

    def is_full(self):
        if self.data_count < self.max_period:
            return False
        return True