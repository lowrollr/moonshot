'''
FILE: unique_3_river.py
AUTHORS:
    -> Ross Copeland (rhcopeland101@gmail.com)
WHAT:
    -> This file contains the Unique 3 River Pattern Indicator
'''
from v2.utils import findParams
from v2.strategy.indicators.param import Param
from v2.strategy.indicators.indicator import Indicator
from talib import CDLUNIQUE3RIVER as talib_CDLUNIQUE3RIVER

'''
CLASS: CDLUNIQUE3RIVER
WHAT:
    -> Implements the Unique 3 River Pattern Indicator and adds the approprite columns to the dataset
    -> What is Unique 3 River Pattern? --> https://www.investopedia.com/terms/u/unique-three-river.asp
    -> Params Required:
        -> 'N/A'
'''
class CDLUNIQUE3RIVER(Indicator):
    
    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: N/A
    RETURN:
        -> name of the column
    WHAT: 
        -> computes the Unique 3 River Pattern
    TODO:
        -> This has not been tested
    '''
    def genData(self, dataset, gen_new_values=True):

        dataset[self.name] = talib_CDLUNIQUE3RIVER(dataset.open, dataset.high, dataset.low, dataset.close)

        return [self.name]
        
    def setDefaultParams(self):
        pass
