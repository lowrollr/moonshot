'''
FILE: stalled_pattern.py
AUTHORS:
    -> Ross Copeland (rhcopeland101@gmail.com)
WHAT:
    -> This file contains the Stalled Pattern Indicator
'''
from v2.utils import findParams
from v2.strategy.indicators.param import Param
from v2.strategy.indicators.indicator import Indicator
from talib import CDLSTALLEDPATTERN as talib_CDLSTALLEDPATTERN

'''
CLASS: CDLSTALLEDPATTERN
WHAT:
    -> Implements the Stalled Pattern Indicator and adds the approprite columns to the dataset
    -> What is Stalled Pattern? --> https://www.investopedia.com/terms/s/stalled-pattern.asp
    -> Params Required:
        -> 'N/A'
'''
class CDLSTALLEDPATTERN(Indicator):
    
    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: N/A
    RETURN:
        -> name of the column
    WHAT: 
        -> computes the Stalled Pattern
    TODO:
        -> This has not been tested
    '''
    def genData(self, dataset, gen_new_values=True):

        dataset[self.name] = talib_CDLSTALLEDPATTERN(dataset.open, dataset.high, dataset.low, dataset.close)

        return [self.name]
        
    def setDefaultParams(self):
        pass
