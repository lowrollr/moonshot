'''
FILE: tristar.py
AUTHORS:
    -> Ross Copeland (rhcopeland101@gmail.com)
WHAT:
    -> This file contains the Tristar Pattern Indicator
'''
from v2.utils import findParams
from v2.strategy.indicators.param import Param
from v2.strategy.indicators.indicator import Indicator
from talib import CDLTRISTAR as talib_CDLTRISTAR

'''
CLASS: CDLTRISTAR
WHAT:
    -> Implements the Tristar Pattern Indicator and adds the approprite columns to the dataset
    -> What is Tristar Pattern? --> https://patternswizard.com/tri-star-candlestick-pattern/
    -> Params Required:
        -> 'N/A'
'''
class CDLTRISTAR(Indicator):
    
    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: N/A
    RETURN:
        -> name of the column
    WHAT: 
        -> computes the Tristar Pattern
    TODO:
        -> This has not been tested
    '''
    def genData(self, dataset, gen_new_values=True):

        dataset[self.name] = talib_CDLTRISTAR(dataset.open, dataset.high, dataset.low, dataset.close)

        return [self.name]
        
    def setDefaultParams(self):
        pass
