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
from v2.strategy.indicators.variance import Variance
from v2.strategy.indicators.slope import Slope
from v2.strategy.indicators.indicator import Indicator
from v2.strategy.indicators.optimal import Optimal
from v2.strategy.indicators.notebook_utils import genDataForAll, fetchIndicators


class indicator_test(Strategy):
    def __init__(self):
        self.name = 'indicator_test'
        self.is_ml = False
        # self.diff = Param(0.01, 0.1, 2, 'diff', 0.02)
        # sma_period = Param(5, 10000, 0, 'period',90)
        # smma_period = Param(5, 10000, 0, 'period', 90)
        # ema_period = Param(5, 10000, 0, 'period', 90)
        # boll_period = Param(5, 10000, 0, 'period', 90)
        # rsi_period = Param(5, 10000, 0, 'period', 90)
        # stoch_highlow = Param(5, 10000, 0, 'highlow_range', 90)
        # stoch_k = Param(5, 10000, 0, 'k_period', 270)
        # macd_ema_slow = Param(5, 10000, 0, 'ema_slow', 120)
        # macd_ema_fast = Param(5, 10000, 0, 'ema_fast', 60)
        # macd_signal = Param(5, 10000, 0, 'signal', 90)
        # pp_period = Param(5, 10000, 0, 'period', 37.0)
        # var_period = Param(5, 10000, 0, 'period', 90)
        # slope_period = Param(5, 10001, 0, 'period', 60)
        # optimal_penalty = Param(0, 0, 0, 'penalty', 0.0026)
        
        # self.indicators = [Indicator(_params=[self.diff], _name='diff'), SMA(_params=[sma_period]), SMMA(_params=[smma_period]), EMA(_params=[ema_period]), BollingerBands(_params=[boll_period]), RSI(_params=[rsi_period]), StochasticOscillator(_params=[stoch_highlow, stoch_k]), MACD(_params=[macd_ema_fast, macd_ema_slow, macd_signal]), PivotPoints(_params=[pp_period]), Slope(_params=[slope_period]), Variance(_params=[var_period]), Optimal(_params=[optimal_penalty])]
        # self.indicators = [Optimal(_params=[optimal_penalty])]
        self.indicators = fetchIndicators(['macd'])

    def process(self, data):
        pass

    def calc_entry(self, data):
        return False

    def calc_exit(self, data):
        return False
        
