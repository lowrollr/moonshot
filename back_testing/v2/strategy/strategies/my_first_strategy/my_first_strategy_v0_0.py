'''
FILE: my_first_strategy_v0_0.py
AUTHORS:
    -> Jacob Marshall (marshingjay@gmail.com)
WHAT:
    -> This file is used for the testing and debugging of indicators
'''
from v2.strategy.strategies.strategy import Strategy
from v2.strategy.indicators.param import Param
from v2.strategy.indicators.ultimate_oscillator import UltimateOscillator
import numpy as np

'''
CLASS: my_first_strategy
WHAT:
    -> test
'''

class my_first_strategy(Strategy):
    '''
    ARGS:
        -> None
    RETURN:
        -> None
    WHAT: 
        -> calculates and adds the indicators to self.indicators to be tested
    '''
    def __init__(self, entry_models=[], exit_models=[]):
        super().__init__(entry_models, exit_models)
        # wanna test some indicators?
        # do that here 

    def process(self, data):
        return

    def calc_entry(self, data):
        time = data.time
        prediction = self.entry_models[1]['results'][time]
        model_1_data = np.array([getattr(data, x) for x in self.entry_models[1]['features']])
        if prediction:
            return True
        else:
            return False

    def calc_exit(self, data):
        time = data.time
        prediction = self.exit_models[1]['results'][time]
        model_1_data = np.array([getattr(data, x) for x in self.exit_models[1]['features']])
        if prediction:
            return True
        else:
            return False
        
