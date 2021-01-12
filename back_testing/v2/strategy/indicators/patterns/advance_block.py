'''
FILE: advance_block.py
AUTHORS:
    -> Ross Copeland (rhcopeland101@gmail.com)
WHAT:
    -> This file contains the Advance Block Indicator
'''
from v2.utils import findParams
from v2.strategy.indicators.param import Param
from v2.strategy.indicators.indicator import Indicator
from talib import CDLADVANCEBLOCK as talib_CDLADVANCEBLOCK

'''
CLASS: CDLADVANCEBLOCK
WHAT:
    -> Implements the Advance Block Pattern Indicator and adds the approprite columns to the dataset
    -> What is Advance Block Pattern? --> https://www.investopedia.com/terms/a/advance-block.asp
    -> Params Required:
        -> 'N/A'
'''
class CDLADVANCEBLOCK(Indicator):
    
    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: N/A
    RETURN:
        -> name of the column
    WHAT: 
        -> computes the Advance Block Pattern
    TODO:
        -> This has not been tested
    '''
    def genData(self, dataset, gen_new_values=True):

        dataset[self.name] = talib_CDLADVANCEBLOCK(dataset.open, dataset.high, dataset.low, dataset.close)

        return [self.name]
        
    def setDefaultParams(self):
        pass
