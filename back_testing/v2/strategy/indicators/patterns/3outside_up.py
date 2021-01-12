'''
FILE: 3outside_up.py
AUTHORS:
    -> Ross Copeland (rhcopeland101@gmail.com)
WHAT:
    -> This file contains the 3 Outside Up/Down Indicator
'''
from v2.utils import findParams
from v2.strategy.indicators.param import Param
from v2.strategy.indicators.indicator import Indicator
from talib import CDL3OUTSIDE as talib_CDL3OUTSIDE

'''
CLASS: CDL3OUTSIDE
WHAT:
    -> Implements the 3 Outside Up/Down Pattern Indicator and adds the approprite columns to the dataset
    -> What is 3 Outside Up/Down Pattern? --> https://www.investopedia.com/terms/t/three-inside-updown.asp
    -> Params Required:
        -> 'N/A'
'''
class CDL3OUTSIDE(Indicator):
    
    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: N/A
    RETURN:
        -> name of the column
    WHAT: 
        -> computes the 3 Outside Up/Down Pattern
    TODO:
        -> This has not been tested
    '''
    def genData(self, dataset, gen_new_values=True):

        dataset[self.name] = talib_CDL3OUTSIDE(dataset.open, dataset.high, dataset.low, dataset.close)

        return [self.name]
        
    def setDefaultParams(self):
        pass
