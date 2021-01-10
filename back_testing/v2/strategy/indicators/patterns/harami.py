'''
FILE: harami.py
AUTHORS:
    -> Ross Copeland (rhcopeland101@gmail.com)
WHAT:
    -> This file contains the Harami Pattern Indicator
'''
from v2.utils import findParams
from v2.strategy.indicators.param import Param
from v2.strategy.indicators.indicator import Indicator
from talib import CDLHARAMI as talib_CDLHARAMI

'''
CLASS: CDLHARAMI
WHAT:
    -> Implements the Harami Pattern Indicator and adds the approprite columns to the dataset
    -> What is Harami Pattern? --> https://www.perfecttrendsystem.com/blog_mt4_1/en/harami-indicator-for-mt4
    -> Params Required:
        -> 'N/A'
'''
class CDLHARAMI(Indicator):
    
    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: N/A
    RETURN:
        -> name of the column
    WHAT: 
        -> computes the Harami Pattern Indicator
    TODO:
        -> This has not been tested
    '''
    def genData(self, dataset, gen_new_values=True):

        dataset[self.name] = talib_CDLHARAMI(dataset.open, dataset.high, dataset.low, dataset.close)

        return [self.name]
        
    def setDefaultParams(self):
        pass
   




