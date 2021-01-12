'''
FILE: 3inside_up.py
AUTHORS:
    -> Ross Copeland (rhcopeland101@gmail.com)
WHAT:
    -> This file contains the 3 Inside Up/Down Indicator
'''
from v2.utils import findParams
from v2.strategy.indicators.param import Param
from v2.strategy.indicators.indicator import Indicator
from talib import CDL3INSIDE as talib_CDL3INSIDE

'''
CLASS: CDL3INSIDE
WHAT:
    -> Implements the 3 Inside Up/Down Pattern Indicator and adds the approprite columns to the dataset
    -> What is 3 Inside Up/Down Pattern? --> https://www.investopedia.com/terms/t/three-inside-updown.asp
    -> Params Required:
        -> 'N/A'
'''
class CDL3INSIDE(Indicator):
    
    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: N/A
    RETURN:
        -> name of the column
    WHAT: 
        -> computes the 3 Inside Up/Down Pattern
    TODO:
        -> This has not been tested
    '''
    def genData(self, dataset, gen_new_values=True):

        dataset[self.name] = talib_CDL3INSIDE(dataset.open, dataset.high, dataset.low, dataset.close)

        return [self.name]
        
    def setDefaultParams(self):
        pass
