'''
FILE: morning_doji_star.py
AUTHORS:
    -> Ross Copeland (rhcopeland101@gmail.com)
WHAT:
    -> This file contains the Morning Doji Star Indicator
'''
from v2.utils import findParams
from v2.strategy.indicators.param import Param
from v2.strategy.indicators.indicator import Indicator
from talib import CDLMORNINGDOJISTAR as talib_CDLMORNINGDOJISTAR

'''
CLASS: CDLMORNINGDOJISTAR
WHAT:
    -> Implements the Morning Doji Star Pattern Indicator and adds the approprite columns to the dataset
    -> What is Morning Doji Star Pattern? --> https://www.candlescanner.com/candlestick-patterns/morning-doji-star/
    -> Params Required:
        -> 'N/A'
'''
class CDLMORNINGDOJISTAR(Indicator):
    
    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: N/A
    RETURN:
        -> name of the column
    WHAT: 
        -> computes the Morning Doji Star Pattern
    TODO:
        -> This has not been tested
    '''
    def genData(self, dataset, gen_new_values=True):

        dataset[self.name] = talib_CDLMORNINGDOJISTAR(dataset.open, dataset.high, dataset.low, dataset.close)

        return [self.name]
        
    def setDefaultParams(self):
        pass
