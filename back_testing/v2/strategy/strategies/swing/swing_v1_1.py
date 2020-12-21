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
        self.diff_up = Param(0.01, 0.1, 2, 'diff_up', 0.02)
        self.diff_down = Param(0.01, 0.1, 2, 'diff_down', 0.02)
        self.up_macd = Param(0.01, 0.1, 2, 'up_macd', 0.09)
        self.down_macd = Param(0.01, 0.1, 2, 'down_macd', 0.04)
        self.stop_loss = 0.0
        self.entry = 0.0
        sma_period = Param(5, 10000, 0, 'period', 30.0)
        ema_fast = Param(5, 10000, 0, 'ema_fast', 3213)
        ema_slow= Param(6, 10001, 0, 'ema_slow', 6445)
        signal = Param(5, 10001, 0, 'signal', 5371)
        
        self.indicators = [MACD(_params=[ema_fast, ema_slow, signal], _name='macd'), Indicator(_params=[self.up_macd, self.down_macd], _name="macd_per"), Indicator(_params=[self.diff_up, self.diff_down], _name='diff'), SMMA(_params=[sma_period], _name='sma')]
    

    def process(self, data):
        if data.close > 1.01 * self.entry:
            self.stop_loss = max(self.stop_loss, data.close + (data.close - self.entry / 2))
        else:
            self.stop_loss = max(self.stop_loss, 0.95 * self.entry)
        pass

    def calc_entry(self, data):
        if data.macd > data.signal + (data.macd * self.up_macd.value):
            if data.close < (data.sma * (1- self.diff_up.value)):
                self.entry = data.close
                return True
            else:
                return False

    def calc_exit(self, data):
        if data.macd < data.signal - (data.macd * self.down_macd.value):
            return True
        elif data.close > (data.sma * (1 + self.diff_down.value)):
            return True
        else:
            return False
        
