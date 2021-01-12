'''
FILE: up_gap3method.py
AUTHORS:
    -> Ross Copeland (rhcopeland101@gmail.com)
WHAT:
    -> This file contains the Upside/Downside Gap 3 Methods Pattern Indicator
'''
from v2.utils import findParams
from v2.strategy.indicators.param import Param
from v2.strategy.indicators.indicator import Indicator
from talib import CDLXSIDEGAP3METHODS as talib_CDLXSIDEGAP3METHODS

'''
CLASS: CDLXSIDEGAP3METHODS
WHAT:
    -> Implements the Upside/Downside Gap 3 Methods Pattern Indicator and adds the approprite columns to the dataset
    -> What is Upside/Downside Gap 3 Methods Pattern? --> https://www.investopedia.com/terms/u/upsidedownside-gap-three-methods.asp
    -> Params Required:
        -> 'N/A'
'''
class CDLXSIDEGAP3METHODS(Indicator):
    
    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: N/A
    RETURN:
        -> name of the column
    WHAT: 
        -> computes the Upside/Downside Gap 3 Methods Pattern
    TODO:
        -> This has not been tested
    '''
    def genData(self, dataset, gen_new_values=True):

        dataset[self.name] = talib_CDLXSIDEGAP3METHODS(dataset.open, dataset.high, dataset.low, dataset.close)

        return [self.name]
        
    def setDefaultParams(self):
        pass
