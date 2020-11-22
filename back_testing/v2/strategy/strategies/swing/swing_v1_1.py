'''
FILE: swing_v1_0.py
AUTHORS:
    -> Jacob Marshall (marshingjay@gmail.com)
WHAT:
    -> This is version 1.1 of the swing algorithm
    -> see key changes in class header
'''

from v2.strategy.strategies.strategy import Strategy
from v2.strategy.indicators.param import Param
from v2.strategy.indicators.smma import SMMA
from v2.strategy.indicators.macd import MACD
from v2.strategy.indicators.indicator import Indicator

'''
CLASS: swing
WHAT:
    -> Improves upon version 1_0
    -> Implements stop loss
    -> Uses macd to inform buy/sell signals
'''
class swing_v(Strategy):
    def __init__(self):
        self.name = 'swing_v1_1'
        self.is_ml = False
        self.diff = Param(0.01, 0.1, 2, 'diff', 0.05)
        self.stop_loss = 0.0
        self.entry = 0.0
        sma_period = Param(5, 10000, 0, 'period', 73.0)
        ema_fast = Param(5, 10000, 0, 'ema_fast', 410)
        ema_slow= Param(6, 10001, 0, 'ema_slow', 4274)
        signal = Param(5, 10001, 0, 'signal', 3005)
        self.indicators = [MACD(_params=[ema_fast, ema_slow, signal], _name='macd'), Indicator(_params=[self.diff], _name='diff'), SMMA(_params=[sma_period], _name='sma')]
    

    def process(self, data):
        if data.close > 1.01 * self.entry:
            self.stop_loss = max(self.stop_loss, data.close + (data.close - self.entry / 2))
        else:
            self.stop_loss = max(self.stop_loss, 0.95 * self.entry)
        pass

    def calc_entry(self, data):
        if data.macd > data.signal + (data.macd * 0.1):
            if data.close < (data.sma * (1- self.diff.value)):
                self.entry = data.close
                return True
            else:
                return False

    def calc_exit(self, data):
        if data.macd < data.signal - (data.macd * 0.1):
            return True
        elif data.close > (data.sma * (1 + self.diff.value)):
            return True
        else:
            return False
        
