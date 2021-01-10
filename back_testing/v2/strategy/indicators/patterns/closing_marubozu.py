'''
FILE: closing_marubozu.py
AUTHORS:
    -> Ross Copeland (rhcopeland101@gmail.com)
WHAT:
    -> This file contains the Breakaway Indicator
'''
from v2.utils import findParams
from v2.strategy.indicators.param import Param
from v2.strategy.indicators.indicator import Indicator
from talib import CDLCLOSINGMARUBOZU as talib_CDLCLOSINGMARUBOZU

'''
CLASS: CDLCLOSINGMARUBOZU
WHAT:
    -> Implements the Closing Marubozu Pattern Indicator and adds the approprite columns to the dataset
    -> What is Closing Marubozu Pattern? --> https://patternswizard.com/closing-marubozu-candlestick-pattern/
    -> Params Required:
        -> 'N/A'
'''
class CDLCLOSINGMARUBOZU(Indicator):
    
    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: N/A
    RETURN:
        -> name of the column
    WHAT: 
        -> computes the Closing Marubozu Pattern
    TODO:
        -> This has not been tested
    '''
    def genData(self, dataset, gen_new_values=True):

        dataset[self.name] = talib_CDLCLOSINGMARUBOZU(dataset.open, dataset.high, dataset.low, dataset.close)

        return [self.name]
        
    def setDefaultParams(self):
        pass
