'''
FILE: tasuki_gap.py
AUTHORS:
    -> Ross Copeland (rhcopeland101@gmail.com)
WHAT:
    -> This file contains the Tasuki Gap Pattern Indicator
'''
from v2.utils import findParams
from v2.strategy.indicators.param import Param
from v2.strategy.indicators.indicator import Indicator
from talib import CDLTASUKIGAP as talib_CDLTASUKIGAP

'''
CLASS: CDLTASUKIGAP
WHAT:
    -> Implements the Tasuki Gap Pattern Indicator and adds the approprite columns to the dataset
    -> What is Tasuki Gap Pattern? --> https://www.investopedia.com/terms/u/upside-tasuki-gap.asp
    -> Params Required:
        -> 'N/A'
'''
class CDLTASUKIGAP(Indicator):
    
    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: N/A
    RETURN:
        -> name of the column
    WHAT: 
        -> computes the Tasuki Gap Pattern
    TODO:
        -> This has not been tested
    '''
    def genData(self, dataset, gen_new_values=True):

        dataset[self.name] = talib_CDLTASUKIGAP(dataset.open, dataset.high, dataset.low, dataset.close)

        return [self.name]
        
    def setDefaultParams(self):
        pass
