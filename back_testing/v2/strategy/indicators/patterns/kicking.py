'''
FILE: kicking.py
AUTHORS:
    -> Ross Copeland (rhcopeland101@gmail.com)
WHAT:
    -> This file contains the Kicking Pattern Indicator
'''
from v2.utils import findParams
from v2.strategy.indicators.param import Param
from v2.strategy.indicators.indicator import Indicator
from talib import CDLKICKING as talib_CDLKICKING

'''
CLASS: CDLHIKKAKE
WHAT:
    -> Implements the Kicking Pattern Indicator and adds the approprite columns to the dataset
    -> What is Kicking Pattern? --> https://hitandruncandlesticks.com/bullish-kicker-candlestick-pattern/
    -> Params Required:
        -> 'N/A'
'''
class CDLKICKING(Indicator):
    
    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: N/A
    RETURN:
        -> name of the column
    WHAT: 
        -> computes the Kicking Pattern
    TODO:
        -> This has not been tested
    '''
    def genData(self, dataset, gen_new_values=True):

        dataset[self.name] = talib_CDLKICKING(dataset.open, dataset.high, dataset.low, dataset.close)

        return [self.name]
        
    def setDefaultParams(self):
        pass
