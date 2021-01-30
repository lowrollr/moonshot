import os
import pickle
from collections import deque

class DataEngine():
    def __init__(self, coins):
        self.model = None
        self.propba_thresh = 0.0
        self.max_period = 0
        self.features = []
        self.indicators = []
        self.data_count = 0
        self.data_queue = dict()

        self.importModel()

        for coin in coins:
            self.data_queue[coin]['open'] = deque(maxlen=self.max_period)
            self.data_queue[coin]['high'] = deque(maxlen=self.max_period)
            self.data_queue[coin]['low'] = deque(maxlen=self.max_period)
            self.data_queue[coin]['close'] = deque(maxlen=self.max_period)
            self.data_queue[coin]['volume'] = deque(maxlen=self.max_period)

    '''
    ASSUMPTIONS:
        -> this is loading one model
        -> that model is a buy model
    '''
    def importModel(self):
            #get the correct model
            model_path = f'saved_models/{os.listdir("saved_models")[0]}'
            mod_obj = pickle.load(open(model_path, 'rb'))

            self.indicators.extend(mod_obj['indicators'])
            self.features.extend(mod_obj['features'])
            self.model = mod_obj['model']
            self.propba_thresh = mod_obj['proba_threshold']

    def is_full(self):
        if self.data_count < self.max_period:
            return False
        return True