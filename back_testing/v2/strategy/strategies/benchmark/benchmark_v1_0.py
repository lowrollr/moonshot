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
from v2.strategy.indicators.roc import RateOfChange
from v2.strategy.indicators.rsi import RSI
from v2.strategy.indicators.cmo import CMO
from v2.strategy.indicators.sma import SMA
from v2.strategy.indicators.roc import RateOfChange
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
    def __init__(self, coin_names, entry_models=[], exit_models=[]):
        super().__init__(entry_models, exit_models)
        sma_90 = SMA(_params=[Param(0,0,0,'period',90)], _value='close', _appended_name='90')
        sma_120 = SMA(_params=[Param(0,0,0,'period',120)], _value='close', _appended_name='120')
        sma_150 = SMA(_params=[Param(0,0,0,'period',150)], _value='close', _appended_name='150')
        sma_180 = SMA(_params=[Param(0,0,0,'period',180)], _value='close', _appended_name='180')
        sma_210 = SMA(_params=[Param(0,0,0,'period',210)], _value='close', _appended_name='210')
        sma_240 = SMA(_params=[Param(0,0,0,'period',240)], _value='close', _appended_name='240')
        sma_270 = SMA(_params=[Param(0,0,0,'period',270)], _value='close', _appended_name='270')
        sma_300 = SMA(_params=[Param(0,0,0,'period',300)], _value='close', _appended_name='300')
        sma_330 = SMA(_params=[Param(0,0,0,'period',330)], _value='close', _appended_name='330')
        sma_360 = SMA(_params=[Param(0,0,0,'period',360)], _value='close', _appended_name='360')
        
        roc = RateOfChange(_params=[Param(0,0,0,'period',30)], _value='close')
        
        
        # boll_bands_long = BollingerBands(_params=[Param(0,0,0,'period',3000)], _value='close', _appended_name='long')
        self.algo_indicators.extend([sma_90, sma_120, sma_150, sma_180, sma_210, sma_240, sma_270, sma_300, sma_330, sma_360, roc])

        self.sma_period = dict()
        # Algorithm-centered class variables
        self.looking_to_enter = dict()
        
        
        self.limit_up = dict()
    
        self.stop_loss = dict()
        
        self.profit_goal = dict()
        
        for x in coin_names:
            self.sma_period[x] = 120
            self.looking_to_enter[x] = False
            
            
            self.limit_up[x] = 0.0
            
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
        if self.looking_to_enter[coin_name] and data.close > self.limit_up[coin_name]:
            
            self.looking_to_enter[coin_name] = False
            # self.stop_loss[coin_name] = data.close * 0.95
        
            # self.profit_goal[coin_name] = data.SMA
            return True
        
        self.looking_to_enter[coin_name] = False
        time = data.time
        prediction = self.entry_models[1][f'{coin_name}_results'][time]
        if prediction and data.close < getattr(data, f'SMA_{self.sma_period[coin_name]}') * (0.97):
            
            self.limit_up[coin_name] = data.close * 1.005
            self.looking_to_enter[coin_name] = True
            
        return False

    def calc_exit(self, data, coin_name):
        
        if data.close > getattr(data, f'SMA_{self.sma_period[coin_name]}'):
            
            self.stop_loss[coin_name] = max(self.stop_loss[coin_name], data.close * 0.995)
       
        if data.close < self.stop_loss[coin_name]:
            self.stop_loss[coin_name] = 0.0
            if data.RateOfChange < 0:
                self.sma_period[coin_name] = 90
            elif data.RateOfChange < 0.02:
                self.sma_period[coin_name] = max(90, self.sma_period[coin_name] - 30)
            elif data.RateOfChange < 0.04:
                pass
            else:
                self.sma_period[coin_name] = min(360, self.sma_period[coin_name] + 30)
            return True
        
        return False
        
    # def getSMABucket(self, variance):
    #     if 