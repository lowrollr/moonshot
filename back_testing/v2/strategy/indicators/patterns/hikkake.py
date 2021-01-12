'''
FILE: hikkake.py
AUTHORS:
    -> Ross Copeland (rhcopeland101@gmail.com)
WHAT:
    -> This file contains the Hikakke Pattern Indicator
'''
from v2.utils import findParams
from v2.strategy.indicators.param import Param
from v2.strategy.indicators.indicator import Indicator
from talib import CDLHIKKAKE as talib_CDLHIKKAKE

'''
CLASS: CDLHIKKAKE
WHAT:
    -> Implements the Hikkake Pattern Indicator and adds the approprite columns to the dataset
    -> What is Hikkake? --> https://www.investopedia.com/terms/h/hikkakepattern.asp
    -> Params Required:
        -> 'N/A'
'''
class CDLHIKKAKE(Indicator):
    
    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: N/A
    RETURN:
        -> name of the column
    WHAT: 
        -> computes the Hikkake Indicator
    TODO:
        -> This has not been tested
    '''
    def genData(self, dataset, gen_new_values=True):

        dataset[self.name] = talib_CDLHIKKAKE(dataset.open, dataset.high, dataset.low, dataset.close)

        return [self.name]
        
    def setDefaultParams(self):
        pass
   




