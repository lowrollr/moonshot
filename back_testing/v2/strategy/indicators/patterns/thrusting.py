'''
FILE: thrusting.py
AUTHORS:
    -> Ross Copeland (rhcopeland101@gmail.com)
WHAT:
    -> This file contains the Thrusting Pattern Indicator
'''
from v2.utils import findParams
from v2.strategy.indicators.param import Param
from v2.strategy.indicators.indicator import Indicator
from talib import CDLTHRUSTING as talib_CDLTHRUSTING

'''
CLASS: CDLTHRUSTING
WHAT:
    -> Implements the Thrusting Pattern Indicator and adds the approprite columns to the dataset
    -> What is Thrusting Pattern? --> https://tradingsim.com/blog/thrusting-line/
    -> Params Required:
        -> 'N/A'
'''
class CDLTHRUSTING(Indicator):
    
    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: N/A
    RETURN:
        -> name of the column
    WHAT: 
        -> computes the Thrusting Pattern
    TODO:
        -> This has not been tested
    '''
    def genData(self, dataset, gen_new_values=True):

        dataset[self.name] = talib_CDLTHRUSTING(dataset.open, dataset.high, dataset.low, dataset.close)

        return [self.name]
        
    def setDefaultParams(self):
        pass
