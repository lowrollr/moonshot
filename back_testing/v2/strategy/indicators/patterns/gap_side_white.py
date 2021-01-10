'''
FILE: gap_side_white.py
AUTHORS:
    -> Ross Copeland (rhcopeland101@gmail.com)
WHAT:
    -> This file contains the Up/Down-gap side-by-side white lines Indicator
'''
from v2.utils import findParams
from v2.strategy.indicators.param import Param
from v2.strategy.indicators.indicator import Indicator
from talib import CDLGAPSIDESIDEWHITE as talib_CDLGAPSIDESIDEWHITE

'''
CLASS: CDLGAPSIDESIDEWHITE
WHAT:
    -> Implements the Up/Down-gap side-by-side white lines Pattern Indicator and adds the approprite columns to the dataset
    -> What is Up/Down-gap side-by-side white lines Pattern? --> https://www.investopedia.com/terms/u/updown-gap-sidebyside-white-lines.asp
    -> Params Required:
        -> 'N/A'
'''
class CDLGAPSIDESIDEWHITE(Indicator):
    
    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: N/A
    RETURN:
        -> name of the column
    WHAT: 
        -> computes the Up/Down-gap side-by-side white lines Pattern
    TODO:
        -> This has not been tested
    '''
    def genData(self, dataset, gen_new_values=True):

        dataset[self.name] = talib_CDLGAPSIDESIDEWHITE(dataset.open, dataset.high, dataset.low, dataset.close)

        return [self.name]
        
    def setDefaultParams(self):
        pass
