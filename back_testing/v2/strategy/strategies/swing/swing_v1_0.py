'''
FILE: swing_v1_0.py
AUTHORS:
    -> Jacob Marshall (marshingjay@gmail.com)
WHAT:
    -> This is version 1.0 of the swing algorithm
'''

from v2.strategy.strategies.strategy import Strategy
from v2.strategy.indicators.param import Param
from v2.strategy.indicators.smma import SMMA
from v2.strategy.indicators.indicator import Indicator


'''
CLASS: swing
WHAT:
    -> Implements the swing strategy
    -> buys when price is x% below simple moving average
    -> sells when price is x% above simple moving average
'''
class swing(Strategy):

    '''
    ARGS:
        -> None
    RETURN:
        -> None
    WHAT: 
        -> initializes approprtiate params and indicators
        
    '''
    def __init__(self):
        self.name = 'swing'
        self.is_ml = False
        # represents % above or below sma we should buy or sell at
        self.diff = Param(0.01, 0.1, 2, 'diff', 0.02)
        sma_period = Param(5, 10000, 0, 'period', 37.0)
        self.indicators = [Indicator(_params=[self.diff], _name='diff'), SMMA(_params=[sma_period], _name='sma')]

    '''
    ARGS:
        -> data (Tuple): a single row from a dataframe
    RETURN:
        -> None
    WHAT: 
        -> no tick-by-tick processing required
    '''
    def process(self, data):
        pass

    '''
    ARGS:
        -> data (Tuple): a single row from a dataframe
    RETURN:
        -> (Boolean): if we should enter a position
    WHAT: 
        -> checks if the current price fulfills the buy condition
    '''
    def calc_entry(self, data):
        if data.close < (data.sma * (1- self.diff.value)):
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
        if data.close > (data.sma * (1 + self.diff.value)):
            return True
        else:
            return False
        
