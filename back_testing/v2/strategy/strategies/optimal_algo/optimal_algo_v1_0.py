import pickle
import pandas as pd
import numpy as np

from v2.strategy.strategies.strategy import Strategy
from v2.strategy.indicators.param import Param
from v2.strategy.indicators.indicator import Indicator

from v2.strategy.indicators.rsi import RSI
from v2.strategy.indicators.macd import MACD
from v2.strategy.indicators.slope import Slope
from v2.strategy.indicators.variance import Variance
from v2.strategy.indicators.stochastic_oscillator import StochasticOscillator



class optimal_algo_v1_0(Strategy):

    def __init__(self):
        print('using optimal_algo_v1_0 strategy')
        self.is_ml = False
        self.name = 'optimal_v1.0'

        self.sell_model = pickle.loads(open('./v2/strategy/saved_models/optimal_algo_v1_0.py', 'rb'))

        stoch_highlow = Param(5, 10000, 0, 'highlow_range', 90.0)
        stoch_k = Param(5, 10000, 0, 'k_period', 270.0)
        stoch_oscillator = StochasticOscillator(_params=[stoch_highlow, stoch_k])

        rsi_period = Param(5, 10000, 0, 'period', 90.0)
        rsi_ = RSI(_params=[rsi_period])

        ema_fast = Param(5, 10000, 0, 'ema_fast', 60)
        ema_slow= Param(6, 10001, 0, 'ema_slow', 120)
        signal = Param(5, 10001, 0, 'signal', 90)
        macd_ = MACD(_params=[ema_fast, ema_slow, signal])

        slope_period = Param(5, 10001, 0, 'period', 30)
        slope = Slope(_params=[slope_period])

        var_period = Param(5, 10001, 0, 'period', 60)
        variance = Variance(_params=[var_period])

        self.indicators = [macd_, rsi_, slope, stoch_oscillator, variance]
        self.fees = 0.0026
        self.looking_for_exit = False
        self.looking_for_entry = False
        self.stop_loss = 0.0
        self.trailing_entry = 0.0

    def process(self, data):
        if self.looking_for_exit:
            self.stop_loss = max(self.stop_loss, 0.995 * data.close)
        elif self.looking_for_entry:
            self.trailing_entry = min(self.trailing_entry, 1.005 * data.close)
        
            

    
    def calc_entry(self, data):
        if 

    def calc_exit(self, data):
        if self.looking_for_exit and (data.close < self.stop_loss):
            self.looking_for_exit = False
            return True
        rf_model_data = np.array([data.close, data.rsi, data.MACD, data.stosc_k, data.stosc_d, data.slope, data.variance])
        rf_model_predict = 0
        if not np.isnan(np.sum(rf_model_data)):
            rf_model_data = rf_model_data.reshape(1, -1)
            rf_model_predict = self.sell_model.predict(rf_model_data)[0]
        if rf_model_predict:
            self.looking_for_exit = True
            self.stop_loss = 0.995 * data.close
        return False

