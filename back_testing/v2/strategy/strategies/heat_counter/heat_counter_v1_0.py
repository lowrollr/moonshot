'''
FILE: heat_counter_v1_0.py
AUTHORS:
    -> Jacob Marshall (marshingjay@gmail.com)
WHAT:
    -> This is version 1.0 of the heat counter algorithm
'''
import pickle
from collections import deque
import numpy as np

from v2.strategy.strategies.strategy import Strategy
from v2.strategy.indicators.param import Param
from v2.strategy.indicators.indicator import Indicator
from v2.strategy.indicators.rsi import RSI
from v2.strategy.indicators.macd import MACD
from v2.strategy.indicators.slope import Slope
from v2.strategy.indicators.variance import Variance
from v2.strategy.indicators.stochastic_oscillator import StochasticOscillator

'''
CLASS: Swing_1_0
WHAT:
    -> Implements the swing strategy
    -> buys when price is x% below simple moving average
    -> sells when price is x% above simple moving average
'''
class HeatCounter(Strategy):

    '''
    ARGS:
        -> None
    RETURN:
        -> None
    WHAT: 
        -> initializes approprtiate params and indicators   
    '''
    def __init__(self):
        self.name = 'heat_counter'
        self.is_ml = False
        self.hour_queue = deque(maxlen=60)
        self.little_queue = deque(maxlen=480)
        self.rolling_little = deque(maxlen=480)
        self.big_queue = deque(maxlen=1440)
        self.rolling_big = deque(maxlen=1440)
        # represents % above or below sma we should buy or sell at
        self.diff = Param(0.01, 0.1, 2, 'diff', 0.02)
        sma_period = Param(5, 10000, 0, 'period', 37.0)
        self.bear_model = pickle.load(open('./v2/strategy/saved_models/optimal_v2_buy_rf.sav', 'rb'))
        self.bull_model = pickle.load(open('./v2/strategy/saved_models/optimal_v2_sell_rf.sav', 'rb'))
        self.little_avg = 0 
        self.big_avg = 1440
        self.looking_for_exit = False
        self.stop_loss = 0.0


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

    '''
    ARGS:
        -> data (Tuple): a single row from a dataframe
    RETURN:
        -> None
    WHAT: 
        -> no tick-by-tick processing required
    '''
    def process(self, data):
        bear_model_data = np.array([data.rsi, data.MACD, data.stosc_k, data.stosc_d, data.slope, data.variance])
        bull_model_data = np.array([data.close, data.rsi, data.MACD, data.stosc_k, data.stosc_d, data.slope, data.variance])
        
        bear_value = 0
        if not np.isnan(np.sum(bear_model_data)):
            bear_model_data = bear_model_data.reshape(1, -1)
            prediction = self.bear_model.predict(bear_model_data)[0]
            if prediction:
                bear_value = 1
        bull_value = 0
        if not np.isnan(np.sum(bull_model_data)):
            bull_model_data = bull_model_data.reshape(1, -1)
            prediction = self.bull_model.predict(bull_model_data)[0]
            if prediction:
                bull_value = 1
        if len(self.hour_queue) < 60:
            self.hour_queue.append(bull_value - bear_value)
        else:
            self.hour_queue.popleft()
            self.hour_queue.append(bull_value - bear_value)

        hour_queue_sum = sum(self.hour_queue)
        if len(self.big_queue) < 1440:
            self.big_queue.append(hour_queue_sum)
        else:
            self.big_queue.popleft()
            self.big_queue.append(hour_queue_sum)
            self.big_avg = float(sum(self.big_queue)) / 1440.0
        if len(self.little_queue) < 480:
            self.little_queue.append(hour_queue_sum)
        else:
            self.little_queue.popleft()
            self.little_queue.append(hour_queue_sum)
            self.little_avg = float(sum(self.little_queue)) / 480.0
        if self.stop_loss:
            self.stop_loss = max(self.stop_loss, data.close * 0.999)

    '''
    ARGS:
        -> data (Tuple): a single row from a dataframe
    RETURN:
        -> (Boolean): if we should enter a position
    WHAT: 
        -> checks if the current price fulfills the buy condition
    '''
    def calc_entry(self, data):
        if self.little_avg > self.big_avg:
            return True
        else:
            return False

    '''
    ARGS:
        -> data (Tuple): a single row from a dataframe
    RETURN:
        -> (Boolean): if we should exit a position
    WHAT: 
        -> checks if the current price fulfills the sell condition
    '''
    def calc_exit(self, data):
        # if self.looking_for_exit and (data.close < self.stop_loss):
        #     self.stop_loss = 0.0
        #     self.looking_for_exit = False
        #     return True
        if self.big_avg > self.little_avg and self.little_avg < 0:
            # if not self.looking_for_exit:
            #     self.looking_for_exit = True
            #     self.stop_loss = data.close * 0.999
            # return False
            return True
        else:
            return False
        
