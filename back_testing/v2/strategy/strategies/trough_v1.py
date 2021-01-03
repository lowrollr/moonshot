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
from v2.strategy.indicators.mmroc import MinMaxRateOfChange
from v2.strategy.indicators.variance import Variance
from tensorflow.keras.models import load_model

class trough_v1(Strategy):
    def __init__(self):
        self.is_ml = False
        self.name = 'trough_v1'
        self.stop_loss = 0.0
        self.model_trough = load_model('./v2/strategy/saved_models/boost_rf_lstm.sav')
        self.boost_model = pickle.load(open('./v2/strategy/saved_models/part_boost_lstm.sav', 'rb'))
        self.rf_model = pickle.load(open('./v2/strategy/saved_models/part_rf_lstm.sav', 'rb'))
        self.looking_for_exit = False
        self.looking_for_entry = False
        self.entry_pt_value = 0.0
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
        mmroc_period = Param(5, 10001, 0, 'period', 30)
        mmroc = MinMaxRateOfChange(_params=[mmroc_period], _name='mmroc')
        var_period = Param(5, 10001, 0, 'period', 60)
        stop_loss_param = Param(0, 0, 0, 'stop_loss_percentage', 0)
        variance = Variance(_params=[var_period, stop_loss_param], _name='variance')
        self.indicators = [macd_, rsi_, stoch_oscillator, mmroc, variance]
                

    def process(self, data):
        self.stop_loss = max(self.stop_loss, (1 - (data.stop_loss_percentage / 100)) * data.close)

    def calc_entry(self, data):
        rf_model_data = np.array([data.stosc_k, data.mmroc, data.macd_diff, data.rsi])
        
        if not np.isnan(np.sum(rf_model_data)):
            rf_model_data = rf_model_data.reshape(1, -1)
            rf_model_prediction = self.rf_model.predict(rf_model_data)[0]
        else:
            rf_model_prediction = 0.0

        boost_model_data = np.array([data.stosc_k, data.mmroc, data.macd_diff, data.rsi, rf_model_prediction])
        if not np.isnan(np.sum(boost_model_data)):
            boost_model_data = boost_model_data.reshape(1, -1)
            boost_model_prediction = self.boost_model.predict(boost_model_data)[0]
        else:
            boost_model_prediction = 0.0

        nn_model_data = np.array([data.stosc_k, data.mmroc, data.macd_diff, data.rsi, rf_model_prediction, boost_model_prediction])
        if not np.isnan(np.sum(nn_model_data)):
            nn_model_data = nn_model_data.reshape(1, -1)
            nn_model_data = np.reshape(nn_model_data, (nn_model_data.shape[0], 1, nn_model_data.shape[1]))
            prediction = self.model_trough.predict(nn_model_data)[0][1]
        else:
            prediction = 0.0
        

        if prediction > 0.9:
            print(data.time)
            self.looking_for_entry = True
            self.entry_pt_value = data.close
            return False
        else:
            if self.looking_for_entry:
                if data.close > self.entry_pt_value:
                    self.entry = data.close
                    self.stop_loss = 0.995 * data.close
                    return True
                else:
                    return False
            else:
                return False

        


    def calc_exit(self, data):
        if data.close < self.stop_loss:
            self.looking_for_entry = False
            return True
        else:
            return False