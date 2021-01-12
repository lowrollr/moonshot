'''
FILE: spinning_top.py
AUTHORS:
    -> Ross Copeland (rhcopeland101@gmail.com)
WHAT:
    -> This file contains the Spinning Top Pattern Indicator
'''
from v2.utils import findParams
from v2.strategy.indicators.param import Param
from v2.strategy.indicators.indicator import Indicator
from talib import CDLSPINNINGTOP as talib_CDLSPINNINGTOP

'''
CLASS: CDLSPINNINGTOP
WHAT:
    -> Implements the Spinning Top Pattern Indicator and adds the approprite columns to the dataset
    -> What is Spinning Top Pattern? --> https://patternswizard.com/short-line-candlestick-pattern/
    -> Params Required:
        -> 'N/A'
'''
class CDLSPINNINGTOP(Indicator):
    
    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: N/A
    RETURN:
        -> name of the column
    WHAT: 
        -> computes the Spinning Top Pattern
    TODO:
        -> This has not been tested
    '''
    def genData(self, dataset, gen_new_values=True):

        dataset[self.name] = talib_CDLSPINNINGTOP(dataset.open, dataset.high, dataset.low, dataset.close)

        return [self.name]
        
    def setDefaultParams(self):
        pass
