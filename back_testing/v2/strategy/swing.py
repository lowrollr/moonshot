from v2.strategy.strategy import Strategy
from v2.strategy.indicators.param import Param
from v2.strategy.indicators.smma import SMMA
from v2.strategy.indicators.indicator import Indicator


class swing(Strategy):
    def __init__(self):
        self.sma = 60
        self.name = 'swing'
        self.is_ml = False
        self.diff = Param(0.01, 0.1, 2, 'diff')
        sma_period = Param(5, 10000, 0, 'period')
        self.indicators = [Indicator(_params=[self.diff], _name='diff'), SMMA(_params=[sma_period], _name='sma')]


    def process(self, data):
        pass

    def calc_entry(self, data):
        if data.close < (data.sma * (1- self.diff.value)):
            return True
        else:
            return False

    def calc_exit(self, data):
        if data.close > (data.sma * (1 + self.diff.value)):
            return True
        else:
            return False
        
