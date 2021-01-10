'''
FILE: belt_hold.py
AUTHORS:
    -> Ross Copeland (rhcopeland101@gmail.com)
WHAT:
    -> This file contains the Belt Hold Indicator
'''
from v2.utils import findParams
from v2.strategy.indicators.param import Param
from v2.strategy.indicators.indicator import Indicator
from talib import CDLBELTHOLD as talib_CDLBELTHOLD

'''
CLASS: CDLBELTHOLD
WHAT:
    -> Implements the Belt Hold Pattern Indicator and adds the approprite columns to the dataset
    -> What is Belt Hold Pattern? --> https://www.investopedia.com/terms/b/bullishbelthold.asp
    -> Params Required:
        -> 'N/A'
'''
class CDLBELTHOLD(Indicator):
    
    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: N/A
    RETURN:
        -> name of the column
    WHAT: 
        -> computes the Belt Hold Pattern
    TODO:
        -> This has not been tested
    '''
    def genData(self, dataset, gen_new_values=True):

        dataset[self.name] = talib_CDLBELTHOLD(dataset.open, dataset.high, dataset.low, dataset.close)

        return [self.name]
        
    def setDefaultParams(self):
        pass
