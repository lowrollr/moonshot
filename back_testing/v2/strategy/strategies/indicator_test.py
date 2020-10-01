from v2.strategy.strategies.strategy import Strategy
from v2.strategy.indicators.param import Param
from v2.strategy.indicators.smma import SMMA
from v2.strategy.indicators.sma import SMA
from v2.strategy.indicators.ema import EMA
from v2.strategy.indicators.rsi import RSI
from v2.strategy.indicators.bollinger_bands import BollingerBands
from v2.strategy.indicators.stochastic_oscillator import StochasticOscillator
from v2.strategy.indicators.macd import MACD
from v2.strategy.indicators.pivot_points import PivotPoints
from v2.strategy.indicators.indicator import Indicator


class swing(Strategy):
    def __init__(self):
        self.name = 'swing'
        self.is_ml = False
        self.diff = Param(0.01, 0.1, 2, 'diff', 0.02)
        sma_period = Param(5, 10000, 0, 'period', 37.0)
        smma_period = Param(5, 10000, 0, 'period', 37.0)
        ema_period = Param(5, 10000, 0, 'period', 37.0)
        boll_period = Param(5, 10000, 0, 'period', 37.0)
        rsi_period = Param(5, 10000, 0, 'period', 37.0)
        stoch_highlow = Param(5, 10000, 0, 'highlow_range', 37.0)
        stoch_k = Param(5, 10000, 0, 'k_period', 37.0)
        macd_ema_slow = Param(5, 10000, 0, 'ema_slow', 37.0)
        macd_ema_fast = Param(5, 10000, 0, 'ema_fast', 37.0)
        macd_signal = Param(5, 10000, 0, 'signal', 37.0)
        pp_period = Param(5, 10000, 0, 'period', 37.0)
        self.indicators = [Indicator(_params=[self.diff], _name='diff'), SMA(_params=[sma_period]), SMMA(_params=[smma_period]), EMA(_params=[ema_period]), BollingerBands(_params=[boll_period]), RSI(_params=[rsi_period]), StochasticOscillator(_params=[stoch_highlow, stoch_k]), MACD(_params=[macd_ema_fast, macd_ema_slow, macd_signal]), PivotPoints(_params=[pp_period])]

    def process(self, data):
        pass

    def calc_entry(self, data):
        return False

    def calc_exit(self, data):
        return False
        
