'''
FILE: marubozu.py
AUTHORS:
    -> Ross Copeland (rhcopeland101@gmail.com)
WHAT:
    -> This file contains the Matching Low Indicator
'''
from v2.utils import findParams
from v2.strategy.indicators.param import Param
from v2.strategy.indicators.indicator import Indicator
from talib import CDLMATCHINGLOW as talib_CDLMATCHINGLOW

'''
CLASS: CDLMATCHINGLOW
WHAT:
    -> Implements the Matching Low Pattern Indicator and adds the approprite columns to the dataset
    -> What is Matching Low Pattern? --> https://www.investopedia.com/terms/m/matching-low.asp
    -> Params Required:
        -> 'N/A'
'''
class CDLMATCHINGLOW(Indicator):
    
    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: N/A
    RETURN:
        -> name of the column
    WHAT: 
        -> computes the Matching Low Pattern
    TODO:
        -> This has not been tested
    '''
    def genData(self, dataset, gen_new_values=True):

        dataset[self.name] = talib_CDLMATCHINGLOW(dataset.open, dataset.high, dataset.low, dataset.close)

        return [self.name]
        
    def setDefaultParams(self):
        pass
