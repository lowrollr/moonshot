'''
FILE: indicator_test_v0_0.py
AUTHORS:
    -> Jacob Marshall (marshingjay@gmail.com)
WHAT:
    -> This file is used for the testing and debugging of indicators
'''
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
from v2.strategy.indicators.optimal_v2 import Optimal_v2
from v2.strategy.indicators.notebook_utils import genDataForAll, fetchIndicators

'''
CLASS: indicator_test
WHAT:
    -> Creates a strategy class that can be specified within the config
    -> This is used so that you can use debugger
    -> Params Required:
        -> None
'''

class indicator_test(Strategy):
    '''
    ARGS:
        -> None
    RETURN:
        -> None
    WHAT: 
        -> calculates and adds the indicators to self.indicators to be tested
    '''
    def __init__(self):
        self.name = 'indicator_test'
        self.is_ml = False
        self.indicators = fetchIndicators(indicator_list=['optimal_v2'], param_specification={'sma.period': 900})

    def process(self, data):
        pass

    def calc_entry(self, data):
        return False

    def calc_exit(self, data):
        return False
        
