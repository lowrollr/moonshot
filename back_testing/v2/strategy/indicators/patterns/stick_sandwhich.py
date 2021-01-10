'''
FILE: stick_sandwhich.py
AUTHORS:
    -> Ross Copeland (rhcopeland101@gmail.com)
WHAT:
    -> This file contains the Stick Sandwhich Pattern Indicator
'''
from v2.utils import findParams
from v2.strategy.indicators.param import Param
from v2.strategy.indicators.indicator import Indicator
from talib import CDLSTICKSANDWICH as talib_CDLSTICKSANDWICH

'''
CLASS: CDLSTICKSANDWICH
WHAT:
    -> Implements the Stick Sandwhich Pattern Indicator and adds the approprite columns to the dataset
    -> What is Stick Sandwhich Pattern? --> https://www.investopedia.com/terms/s/stick-sandwich.asp
    -> Params Required:
        -> 'N/A'
'''
class CDLSTICKSANDWICH(Indicator):
    
    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: N/A
    RETURN:
        -> name of the column
    WHAT: 
        -> computes the Stick Sandwhich Pattern
    TODO:
        -> This has not been tested
    '''
    def genData(self, dataset, gen_new_values=True):

        dataset[self.name] = talib_CDLSTICKSANDWICH(dataset.open, dataset.high, dataset.low, dataset.close)

        return [self.name]
        
    def setDefaultParams(self):
        pass
