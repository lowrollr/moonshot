'''
FILE: long_long_candle_doji.py
AUTHORS:
    -> Ross Copeland (rhcopeland101@gmail.com)
WHAT:
    -> This file contains the Long Line Candle Indicator
'''
from v2.utils import findParams
from v2.strategy.indicators.param import Param
from v2.strategy.indicators.indicator import Indicator
from talib import CDLLONGLINE as talib_CDLLONGLINE

'''
CLASS: CDLLONGLINE
WHAT:
    -> Implements the Long Line Candle Pattern Indicator and adds the approprite columns to the dataset
    -> What is Long Line Candle Pattern? --> https://www.investopedia.com/terms/l/long-legged-doji.asp
    -> Params Required:
        -> 'N/A'
'''
class CDLLONGLINE(Indicator):
    
    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: N/A
    RETURN:
        -> name of the column
    WHAT: 
        -> computes the Long Line Candle Pattern
    TODO:
        -> This has not been tested
    '''
    def genData(self, dataset, gen_new_values=True):

        dataset[self.name] = talib_CDLLONGLINE(dataset.open, dataset.high, dataset.low, dataset.close)

        return [self.name]
        
    def setDefaultParams(self):
        pass
