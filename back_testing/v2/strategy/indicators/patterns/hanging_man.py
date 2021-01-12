'''
FILE: hanging_man.py
AUTHORS:
    -> Ross Copeland (rhcopeland101@gmail.com)
WHAT:
    -> This file contains the Hanging Man Pattern Indicator
'''
from v2.utils import findParams
from v2.strategy.indicators.param import Param
from v2.strategy.indicators.indicator import Indicator
from talib import CDLHANGINGMAN as talib_CDLHANGINGMAN

'''
CLASS: CDLHANGINGMAN
WHAT:
    -> Implements the Hanging Man Pattern Indicator and adds the approprite columns to the dataset
    -> What is Hanging Man Pattern? --> https://www.investopedia.com/articles/active-trading/040914/understanding-hanging-man-optimistic-candlestick-pattern.asp
    -> Params Required:
        -> 'N/A'
'''
class CDLHANGINGMAN(Indicator):
    
    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: N/A
    RETURN:
        -> name of the column
    WHAT: 
        -> computes the Hanging Man Pattern Indicator
    TODO:
        -> This has not been tested
    '''
    def genData(self, dataset, gen_new_values=True):

        dataset[self.name] = talib_CDLHANGINGMAN(dataset.open, dataset.high, dataset.low, dataset.close)

        return [self.name]
        
    def setDefaultParams(self):
        pass
   


