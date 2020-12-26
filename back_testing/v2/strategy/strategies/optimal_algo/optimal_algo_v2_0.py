import pickle
import joblib
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

from v2.strategy.strategies.strategy import Strategy
from v2.strategy.indicators.param import Param
from v2.strategy.indicators.indicator import Indicator

from v2.strategy.indicators.rsi import RSI
from v2.strategy.indicators.macd import MACD
from v2.strategy.indicators.delta import Delta
from v2.strategy.indicators.stochastic_oscillator import StochasticOscillator
from v2.strategy.indicators.optimal_v2 import Optimal_v2




class optimal_algo_v2_0(Strategy):

    def __init__(self):
        print('using optimal_algo_v2_0 strategy')
        self.is_ml = False
        self.name = 'optimal_v2.0'
        self.scaler = joblib.load('./v2/strategy/saved_models/optimal_v3/mm_scalar.sav')
        self.buy_model = pickle.load(open('./v2/strategy/saved_models/optimal_v3/trough_model_v3.pickle', 'rb'))
        self.sell_model = pickle.load(open('./v2/strategy/saved_models/optimal_v3/peak_model_v3.pickle', 'rb'))

        stoch_highlow = Param(5, 10000, 0, 'highlow_range', 360.0)
        stoch_k = Param(5, 10000, 0, 'k_period', 1080.0)
        stoch_oscillator = StochasticOscillator(_params=[stoch_highlow, stoch_k])

        rsi_period = Param(5, 10000, 0, 'period', 360)
        rsi_ = RSI(_params=[rsi_period])

        ema_fast = Param(5, 10000, 0, 'ema_fast', 240)
        ema_slow= Param(6, 10001, 0, 'ema_slow', 480)
        signal = Param(5, 10001, 0, 'signal', 360)
        macd_ = MACD(_params=[ema_fast, ema_slow, signal])

        delta_5_rsi = Delta(_params=[Param(0,0,0,'period', 5)], _appended_name='RSI_5')
        delta_1_rsi = Delta(_params=[Param(0,0,0,'period', 1)], _appended_name='RSI_1')
        delta_10_rsi = Delta(_params=[Param(0,0,0,'period',10)], _appended_name='RSI_10')
        delta_60_rsi = Delta(_params=[Param(0,0,0,'period', 60)], _appended_name='RSI_60')
        
        delta_5_macd = Delta(_params=[Param(0,0,0,'period', 5)], _appended_name='MACD_5')
        delta_1_macd = Delta(_params=[Param(0,0,0,'period', 1)], _appended_name='MACD_1')
        delta_10_macd = Delta(_params=[Param(0,0,0,'period',10)], _appended_name='MACD_10')
        delta_60_macd = Delta(_params=[Param(0,0,0,'period', 60)], _appended_name='MACD_60')

        delta_5_close = Delta(_params=[Param(0,0,0,'period', 5)], _appended_name='close_5')
        delta_1_close = Delta(_params=[Param(0,0,0,'period', 1)], _appended_name='close_1')
        delta_10_close = Delta(_params=[Param(0,0,0,'period',10)], _appended_name='close_10')
        delta_60_close = Delta(_params=[Param(0,0,0,'period', 60)], _appended_name='close_60')

        opt_v2 = Optimal_v2(_params=[])

        self.indicators = [macd_, rsi_, stoch_oscillator, opt_v2, delta_1_macd, delta_5_macd, delta_10_macd, delta_60_macd, delta_1_rsi, delta_5_rsi, delta_10_rsi, delta_60_rsi, delta_1_close, delta_5_close, delta_10_close, delta_60_close]
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
        buy_model_data = np.array([data.RSI, data.MACD, data.stosc_k, data.stosc_d, data.Delta_MACD_1, data.Delta_MACD_5, data.Delta_MACD_10, data.Delta_MACD_60, data.Delta_RSI_1, data.Delta_RSI_5, data.Delta_RSI_10, data.Delta_RSI_60, data.Delta_close_1, data.Delta_close_5, data.Delta_close_10, data.Delta_close_60])
        
        if not np.isnan(np.sum(buy_model_data)):
            buy_model_data = buy_model_data.reshape(1, -1)
            buy_model_data = self.scaler.transform(buy_model_data)
            prediction = self.buy_model.predict(buy_model_data)[0]
        else:
            prediction = 0.0

        if prediction:
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
        sell_model_data = np.array([data.RSI, data.MACD, data.stosc_k, data.stosc_d, data.Delta_MACD_1, data.Delta_MACD_5, data.Delta_MACD_10, data.Delta_MACD_60, data.Delta_RSI_1, data.Delta_RSI_5, data.Delta_RSI_10, data.Delta_RSI_60, data.Delta_close_1, data.Delta_close_5, data.Delta_close_10, data.Delta_close_60])
        
        if not np.isnan(np.sum(sell_model_data)):
            sell_model_data = sell_model_data.reshape(1, -1)
            sell_model_data = self.scaler.transform(sell_model_data)
            
            prediction = self.sell_model.predict(sell_model_data)[0]
        else:
            prediction = 0.0

        if prediction:
            self.looking_for_exit = True
            self.stop_loss= 0.9995 * data.close
        return False

