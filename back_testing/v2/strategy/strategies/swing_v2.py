from v2.strategy.strategies.strategy import Strategy
from v2.strategy.indicators.param import Param
from v2.strategy.indicators.smma import SMMA
from v2.strategy.indicators.macd import MACD
from v2.strategy.indicators.indicator import Indicator


class swing_v2(Strategy):
    def __init__(self):
        self.name = 'swing_v2'
        self.is_ml = False
        self.diff = Param(0.01, 0.1, 2, 'diff', 0.02)
        self.stop_loss = 0.0
        self.stop_loss_active = False
        self.entry = 0.0
        sma_period = Param(5, 10000, 0, 'period', 37.0)
        ema_fast = Param(5, 10000, 0, 'ema_fast', 30)
        ema_slow= Param(6, 10001, 0, 'ema_slow', 60)
        signal = Param(5, 10001, 0, 'signal', 45)
        self.indicators = [MACD(_params=[ema_fast, ema_slow, signal], _name='macd'), Indicator(_params=[self.diff], _name='diff'), SMMA(_params=[sma_period], _name='sma')]
    

    def process(self, data):
        if data.close > 1.01 * self.entry:
            self.calc_entrystop_loss_active = True
        if self.stop_loss_active:
            self.stop_loss = max(self.stop_loss, data.close + (data.close - self.entry / 2))
        pass

    def calc_entry(self, data):
        if data.macd > data.signal + (data.macd * 0.1):
            if data.close < (data.sma * (1- self.diff.value)):
                self.entry = data.close
                self.stop_loss_active = False
                return True
            else:
                return False

    def calc_exit(self, data):
        if data.close > (data.sma * (1 + self.diff.value)) or data.close < self.stop_loss:
            
            return True
        else:
            return False
        
