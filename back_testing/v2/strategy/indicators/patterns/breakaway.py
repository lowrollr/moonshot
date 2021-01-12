'''
FILE: breakaway.py
AUTHORS:
    -> Ross Copeland (rhcopeland101@gmail.com)
WHAT:
    -> This file contains the Breakaway Indicator
'''
from v2.utils import findParams
from v2.strategy.indicators.param import Param
from v2.strategy.indicators.indicator import Indicator
from talib import CDLBREAKAWAY as talib_CDLBREAKAWAY

'''
CLASS: CDLBREAKAWAY
WHAT:
    -> Implements the Breakaway Pattern Indicator and adds the approprite columns to the dataset
    -> What is Breakaway Pattern? --> https://www.instaforex.com/forex_indicators/breakaway
    -> Params Required:
        -> 'N/A'
'''
class CDLBREAKAWAY(Indicator):
    
    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: N/A
    RETURN:
        -> name of the column
    WHAT: 
        -> computes the Breakaway Pattern
    TODO:
        -> This has not been tested
    '''
    def genData(self, dataset, gen_new_values=True):

        dataset[self.name] = talib_CDLBREAKAWAY(dataset.open, dataset.high, dataset.low, dataset.close)

        return [self.name]
        
    def setDefaultParams(self):
        pass
