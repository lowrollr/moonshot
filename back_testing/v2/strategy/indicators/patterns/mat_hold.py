'''
FILE: mat_hold.py
AUTHORS:
    -> Ross Copeland (rhcopeland101@gmail.com)
WHAT:
    -> This file contains the Mat Hold Indicator
'''
from v2.utils import findParams
from v2.strategy.indicators.param import Param
from v2.strategy.indicators.indicator import Indicator
from talib import CDLMATHOLD as talib_CDLMATHOLD

'''
CLASS: CDLMATHOLD
WHAT:
    -> Implements the Mat Hold Pattern Indicator and adds the approprite columns to the dataset
    -> What is Mat Hold Pattern? --> https://www.investopedia.com/terms/m/mat-hold-pattern.asp
    -> Params Required:
        -> 'N/A'
'''
class CDLMATHOLD(Indicator):
    
    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: N/A
    RETURN:
        -> name of the column
    WHAT: 
        -> computes the Mat Hold Pattern
    TODO:
        -> This has not been tested
    '''
    def genData(self, dataset, gen_new_values=True):

        dataset[self.name] = talib_CDLMATHOLD(dataset.open, dataset.high, dataset.low, dataset.close)

        return [self.name]
        
    def setDefaultParams(self):
        pass
