import pickle
import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model

from v2.strategy.strategies.strategy import Strategy
from v2.strategy.indicators.param import Param
from v2.strategy.indicators.indicator import Indicator

from v2.strategy.indicators.rsi import RSI
from v2.strategy.indicators.macd import MACD
from v2.strategy.indicators.mmroc import MinMaxRateOfChange
from v2.strategy.indicators.variance import Variance
from v2.strategy.indicators.stochastic_oscillator import StochasticOscillator
from v2.strategy.indicators.optimal_v2 import Optimal_v2


class optimal_algo_v1_0(Strategy):

    def __init__(self):
        print('using optimal_algo_v1_0 strategy')
        self.is_ml = False
        self.name = 'optimal_v1.0'

        self.sell_model = pickle.load(open('./v2/strategy/saved_models/optimal_v2_sell_rf_90.sav', 'rb'))

        # self.buy_rf = pickle.load(open('./v2/strategy/saved_models/optimal_classify/troughs_random_forest.sav', 'rb'))
        # self.buy_boost = pickle.load(open('./v2/strategy/saved_models/optimal_classify/troughs_boost.sav', 'rb'))
        # self.buy_lstm = load_model('./v2/strategy/saved_models/optimal_classify/troughs_lstm.sav')

        self.buy_lstm = load_model('./v2/strategy/saved_models/boost_rf_lstm.sav')
        self.buy_boost = pickle.load(open('./v2/strategy/saved_models/lstm_trough/part_boost_lstm.sav', 'rb'))
        self.buy_rf = pickle.load(open('./v2/strategy/saved_models/lstm_trough/part_rf_lstm.sav', 'rb'))

        stoch_highlow = Param(5, 10000, 0, 'highlow_range', 90.0)
        stoch_k = Param(5, 10000, 0, 'k_period', 270.0)
        stoch_oscillator = StochasticOscillator(_params=[stoch_highlow, stoch_k])

        rsi_period = Param(5, 10000, 0, 'period', 90.0)
        rsi_ = RSI(_params=[rsi_period])

        ema_fast = Param(5, 10000, 0, 'ema_fast', 60)
        ema_slow= Param(6, 10001, 0, 'ema_slow', 120)
        signal = Param(5, 10001, 0, 'signal', 90)
        macd_ = MACD(_params=[ema_fast, ema_slow, signal])

        mmroc_period = Param(5, 10001, 0, 'period', 30)
        mmroc = MinMaxRateOfChange(_params=[mmroc_period])

        var_period = Param(5, 10001, 0, 'period', 60)
        variance = Variance(_params=[var_period])

        opt_v2 = Optimal_v2(_params=[])
        self.indicators = [macd_, rsi_, mmroc, stoch_oscillator, variance, opt_v2]
        self.looking_for_exit = False
        self.looking_for_entry = False
        self.stop_loss = 0.0
        self.trailing_entry = 0.0

    def process(self, data):
        if self.looking_for_exit:
            self.stop_loss = max(self.stop_loss, 0.9995 * data.close)
        elif self.looking_for_entry:
            self.trailing_entry = min(self.trailing_entry, 1.0005 * data.close)
        
            

    
    def calc_entry(self, data):
        if self.looking_for_entry and (data.close > self.trailing_entry):
            self.looking_for_entry = False
            return True
        rf_model_data = np.array([data.stosc_k, data.mmroc, data.macd_diff, data.rsi])
        
        if not np.isnan(np.sum(rf_model_data)):
            rf_model_data = rf_model_data.reshape(1, -1)
            rf_model_prediction = self.buy_rf.predict(rf_model_data)[0]
        else:
            rf_model_prediction = 0.0

        boost_model_data = np.array([data.stosc_k, data.mmroc, data.macd_diff, data.rsi, rf_model_prediction])
        if not np.isnan(np.sum(boost_model_data)):
            boost_model_data = boost_model_data.reshape(1, -1)
            boost_model_prediction = self.buy_boost.predict(boost_model_data)[0]
        else:
            boost_model_prediction = 0.0

        nn_model_data = np.array([data.stosc_k, data.mmroc, data.macd_diff, data.rsi, rf_model_prediction, boost_model_prediction])
        if not np.isnan(np.sum(nn_model_data)):
            nn_model_data = nn_model_data.reshape(1, -1)
            nn_model_data = np.reshape(nn_model_data, (nn_model_data.shape[0], 1, nn_model_data.shape[1]))
            prediction = self.buy_lstm.predict(nn_model_data)[0][1]
        else:
            prediction = 0.0
        if prediction > 0.9:
            self.looking_for_entry = True
            self.trailing_entry = 1.0005 * data.close
        return False
        # if data.optimal > 0.95:
        #     return True
        # else:
        #     return False

    def calc_exit(self, data):
        if self.looking_for_exit and (data.close < self.stop_loss):
            self.looking_for_exit = False
            return True
        rf_model_data = np.array([data.close, data.rsi, data.MACD, data.stosc_k, data.stosc_d, data.mmroc, data.variance])
        rf_model_predict = 0
        if not np.isnan(np.sum(rf_model_data)):
            rf_model_data = rf_model_data.reshape(1, -1)
            rf_model_predict = self.sell_model.predict(rf_model_data)[0]
        if rf_model_predict:
            self.looking_for_exit = True
            self.stop_loss = 0.9995 * data.close
        return False

