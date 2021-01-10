'''
FILE: doji_star.py
AUTHORS:
    -> Ross Copeland (rhcopeland101@gmail.com)
WHAT:
    -> This file contains the Doji Star Indicator
'''
from v2.utils import findParams
from v2.strategy.indicators.param import Param
from v2.strategy.indicators.indicator import Indicator
from talib import CDLDOJISTAR as talib_CDLDOJISTAR

'''
CLASS: CDLDOJISTAR
WHAT:
    -> Implements the Doji Star Pattern Indicator and adds the approprite columns to the dataset
    -> What is Doji Star Pattern? --> https://www.forexstrategiesresources.com/candlestick-forex-strategies/19-doji-star-system/
    -> Params Required:
        -> 'N/A'
'''
class CDLDOJISTAR(Indicator):
    
    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: N/A
    RETURN:
        -> name of the column
    WHAT: 
        -> computes the Doji Star Pattern
    TODO:
        -> This has not been tested
    '''
    def genData(self, dataset, gen_new_values=True):

        dataset[self.name] = talib_CDLDOJISTAR(dataset.open, dataset.high, dataset.low, dataset.close)

        return [self.name]
        
    def setDefaultParams(self):
        pass
