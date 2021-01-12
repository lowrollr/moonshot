'''
FILE: short_line.py
AUTHORS:
    -> Ross Copeland (rhcopeland101@gmail.com)
WHAT:
    -> This file contains the Short Line Pattern Indicator
'''
from v2.utils import findParams
from v2.strategy.indicators.param import Param
from v2.strategy.indicators.indicator import Indicator
from talib import CDLSHORTLINE as talib_CDLSHORTLINE

'''
CLASS: CDLSHORTLINE
WHAT:
    -> Implements the Short Line Pattern Indicator and adds the approprite columns to the dataset
    -> What is Short Line Pattern? --> https://patternswizard.com/short-line-candlestick-pattern/
    -> Params Required:
        -> 'N/A'
'''
class CDLSHORTLINE(Indicator):
    
    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: N/A
    RETURN:
        -> name of the column
    WHAT: 
        -> computes the Short Line Pattern
    TODO:
        -> This has not been tested
    '''
    def genData(self, dataset, gen_new_values=True):

        dataset[self.name] = talib_CDLSHORTLINE(dataset.open, dataset.high, dataset.low, dataset.close)

        return [self.name]
        
    def setDefaultParams(self):
        pass
