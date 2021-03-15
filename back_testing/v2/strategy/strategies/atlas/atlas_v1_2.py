'''
FILE: benchmark_v0_0.py
AUTHORS:
    -> Jacob Marshall (marshingjay@gmail.com)
WHAT:
    -> This file is used as a benchmark while testing buy models
'''
from v2.strategy.strategies.strategy import Strategy
from v2.strategy.indicators.param import Param
from v2.strategy.indicators.roc import RateOfChange
from v2.strategy.indicators.sma import SMA
import numpy as np


'''
CLASS: Benchmark
WHAT:
    -> test
'''

class Atlas_v1_2(Strategy):
    '''
    ARGS:
        -> None
    RETURN:
        -> None
    WHAT: 
        -> calculates and adds the indicators to self.indicators to be tested
    '''
    def __init__(self, coin_names, entry_models=[], exit_models=[]):
        super().__init__(entry_models, exit_models)
        
        sma_goal = SMA(_params=[Param(0,0,0,'period',150)], _value='close')
        sma_for_roc_short = SMA(_params=[Param(0,0,0,'period',30)], _value='close', _appended_name='for_short')
        
        roc_shorter = RateOfChange(_params=[Param(0,0,0,'period',45)], _value='SMA_for_short', _appended_name='shorter')
        
        self.algo_indicators.extend([sma_goal, sma_for_roc_short, roc_shorter])


        
    
        self.stop_loss = dict()
        
        self.profit_goal = dict()
        
        for x in coin_names:
            
            self.stop_loss[x] = 0.0
            
            self.profit_goal[x] = 0.0
            
        # wanna test some indicators?
        # do that here 

    def process(self, data, coin_name):
        
        # self.stop_loss[coin_name] = max(self.stop_loss[coin_name], data.close * 0.95)
        if self.stop_loss[coin_name]:
            self.stop_loss[coin_name] = max(self.stop_loss[coin_name], data.close * 0.995)
        
        return

    def calc_entry(self, data, coin_name):
        
        
        time = data.time
        prediction = self.entry_models[1][f'{coin_name}_results'][time]
        if data.close < data.SMA * (0.97) and prediction:
            return True
            
        return False

    def calc_exit(self, data, coin_name):
        
        amnt_above = max(-0.01, data.RateOfChange_shorter)
        if data.close > data.SMA * (1 + amnt_above):
            
            self.stop_loss[coin_name] = max(self.stop_loss[coin_name], data.close * 0.999)
       
        if data.close < self.stop_loss[coin_name]:
            self.stop_loss[coin_name] = 0.0
            
            return True
        
        return False