'''
FILE: morning_star.py
AUTHORS:
    -> Ross Copeland (rhcopeland101@gmail.com)
WHAT:
    -> This file contains the Morning Star Indicator
'''
from v2.utils import findParams
from v2.strategy.indicators.param import Param
from v2.strategy.indicators.indicator import Indicator
from talib import CDLMORNINGSTAR as talib_CDLMORNINGSTAR

'''
CLASS: CDLMORNINGSTAR
WHAT:
    -> Implements the Morning Star Pattern Indicator and adds the approprite columns to the dataset
    -> What is Morning Star Pattern? --> https://www.investopedia.com/terms/m/morningstar.asp
    -> Params Required:
        -> 'N/A'
'''
class CDLMORNINGSTAR(Indicator):
    
    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: N/A
    RETURN:
        -> name of the column
    WHAT: 
        -> computes the Morning Star Pattern
    TODO:
        -> This has not been tested
    '''
    def genData(self, dataset, gen_new_values=True):

        dataset[self.name] = talib_CDLMORNINGSTAR(dataset.open, dataset.high, dataset.low, dataset.close)

        return [self.name]
        
    def setDefaultParams(self):
        pass
