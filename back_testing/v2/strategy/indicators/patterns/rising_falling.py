'''
FILE: rising_falling.py
AUTHORS:
    -> Ross Copeland (rhcopeland101@gmail.com)
WHAT:
    -> This file contains the Rising Falling 3 Methods Pattern Indicator
'''
from v2.utils import findParams
from v2.strategy.indicators.param import Param
from v2.strategy.indicators.indicator import Indicator
from talib import CDLRISEFALL3METHODS as talib_CDLRISEFALL3METHODS

'''
CLASS: CDLRISEFALL3METHODS
WHAT:
    -> Implements the Rising Falling 3 Methods Pattern Indicator and adds the approprite columns to the dataset
    -> What is Rising Falling 3 Methods Pattern? --> https://www.investopedia.com/terms/r/rising-three-methods.asp
    -> Params Required:
        -> 'N/A'
'''
class CDLRISEFALL3METHODS(Indicator):
    
    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: N/A
    RETURN:
        -> name of the column
    WHAT: 
        -> computes the Rising Falling 3 Methods Pattern
    TODO:
        -> This has not been tested
    '''
    def genData(self, dataset, gen_new_values=True):

        dataset[self.name] = talib_CDLRISEFALL3METHODS(dataset.open, dataset.high, dataset.low, dataset.close)

        return [self.name]
        
    def setDefaultParams(self):
        pass
