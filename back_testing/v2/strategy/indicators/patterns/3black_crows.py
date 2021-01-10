'''
FILE: 3black_crows.py
AUTHORS:
    -> Ross Copeland (rhcopeland101@gmail.com)
WHAT:
    -> This file contains the 3 Black Crows Pattern Indicator
'''
from v2.utils import findParams
from v2.strategy.indicators.param import Param
from v2.strategy.indicators.indicator import Indicator
from talib import CDL3BLACKCROWS as talib_CDL3BLACKCROWS

'''
CLASS: CDL3BLACKCROWS
WHAT:
    -> Implements the 3 Black Crows Pattern Indicator and adds the approprite columns to the dataset
    -> What is 3 Black Crows Pattern? --> https://www.investopedia.com/terms/t/three_black_crows.asp
    -> Params Required:
        -> 'N/A'
'''
class CDL3BLACKCROWS(Indicator):
    
    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: N/A
    RETURN:
        -> name of the column
    WHAT: 
        -> computes the 3 Black Crows Pattern
    TODO:
        -> This has not been tested
    '''
    def genData(self, dataset, gen_new_values=True):

        dataset[self.name] = talib_CDL3BLACKCROWS(dataset.open, dataset.high, dataset.low, dataset.close)

        return [self.name]
        
    def setDefaultParams(self):
        pass
