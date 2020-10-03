import pickle
import pandas
import numpy as np
from v2.strategy.strategies.strategy import Strategy
from v2.strategy.indicators.param import Param
from v2.strategy.indicators.indicator import Indicator
from sklearn.tree import DecisionTreeClassifier
from v2.strategy.indicators.stochastic_oscillator import StochasticOscillator
from v2.strategy.indicators.bollinger_bands import BollingerBands
from v2.strategy.indicators.rsi import RSI
from v2.strategy.indicators.macd import MACD


class trough_v1(Strategy):
    def __init__(self):
        self.is_ml = False
        self.name = 'trough_v1'
        self.stop_loss = 0.0
        self.model_trough = pickle.load(open('v2/strategy/saved_models/troughs_v3.sav', 'rb'))
        self.model_peak = pickle.load(open('v2/strategy/saved_models/peaks_v3.sav', 'rb'))
        self.looking_for_exit = False
        self.looking_for_entry = False
        self.entry = 0.0
        self.set_new_stop_loss = False
        boll_period = Param(5, 10000, 0, 'period', 90)
        boll_bands = BollingerBands(_params=[boll_period], _name='bollinger_bands')
        stoch_highlow = Param(5, 10000, 0, 'highlow_range', 90.0)
        stoch_k = Param(5, 10000, 0, 'k_period', 270.0)
        stoch_oscillator = StochasticOscillator(_params=[stoch_highlow, stoch_k], _name='stochastic_oscillator')
        rsi_period = Param(5, 10000, 0, 'period', 90.0)
        rsi_ = RSI(_params=[rsi_period], _name='rsi')
        ema_fast = Param(5, 10000, 0, 'ema_fast', 60)
        ema_slow= Param(6, 10001, 0, 'ema_slow', 120)
        signal = Param(5, 10001, 0, 'signal', 90)
        macd_ = MACD(_params=[ema_fast, ema_slow, signal], _name='macd')
        self.indicators = [macd_, rsi_, stoch_oscillator, boll_bands]
                

    def process(self, data):
        self.stop_loss = max(self.stop_loss, 0.99 * data.close)

    def calc_entry(self, data):
        model_data = np.array([data.boll_lower, data.stosc_k, data.macd_diff, data.rsi])
        my_sum = np.sum(model_data)
        if not np.isnan(my_sum):
            model_data = model_data.reshape(1, -1)
            if self.model_trough.predict(model_data):
                self.entry = data.close
                self.looking_for_exit = False
                return True
            else:
                return False
        else:
            return False


    def calc_exit(self, data):
        if self.looking_for_exit:
            if data.close < self.stop_loss:
                return True
            else:
                return False
        else:
            model_data = np.array([data.boll_upper, data.stosc_k, data.macd_diff, data.rsi])
            my_sum = np.sum(model_data)
            if not np.isnan(my_sum):
                model_data = model_data.reshape(1, -1)
                if self.model_peak.predict(model_data):
                    self.stop_loss = 0.99 * data.close
                    self.looking_for_exit = True
                    return False
                else:
                    return False
            else:
                return False
