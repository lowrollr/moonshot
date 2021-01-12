'''
FILE: benchmark_v0_0.py
AUTHORS:
    -> Jacob Marshall (marshingjay@gmail.com)
WHAT:
    -> This file is used as a benchmark while testing buy models
'''
from v2.strategy.strategies.strategy import Strategy
from v2.strategy.indicators.param import Param
from v2.strategy.indicators.ultimate_oscillator import UltimateOscillator
from v2.strategy.indicators.bollinger_bands import BollingerBands
import numpy as np

'''
CLASS: Benchmark
WHAT:
    -> test
'''

class Benchmark(Strategy):
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
        boll_bands = BollingerBands(_params=[Param(0,0,0,'period',100)], _value='close')
        self.algo_indicators.append(boll_bands)
        self.looking_to_enter = False
        self.looking_to_exit = False
        self.limit_up = 0.0
        self.crossed_upper = False
        self.stop_loss = 0.0
        # wanna test some indicators?
        # do that here 

    def process(self, data):
        self.limit_up = min(self.limit_up, data.close * 1.001)
        self.stop_loss = max(self.stop_loss, data.close * 0.99)
        return

    def calc_entry(self, data):
        if self.looking_to_enter and data.close > self.limit_up:
            self.looking_to_enter = False
            self.stop_loss = data.close * 0.99
            return True
        self.looking_to_enter = False
        time = data.time
        prediction = self.entry_models[1]['results'][time]
        if prediction:
            self.limit_up = data.close * 1.001
            self.looking_to_enter = True
        return False

    def calc_exit(self, data):
        if data.close < self.stop_loss:
            self.crossed_upper = False
            return True
        elif data.close < data.boll_upper and self.crossed_upper:
            self.crossed_upper = False
            return True
        elif data.close > data.boll_upper:
            self.crossed_upper = True

        return False
        
