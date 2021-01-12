'''
FILE: shooting_star.py
AUTHORS:
    -> Ross Copeland (rhcopeland101@gmail.com)
WHAT:
    -> This file contains the Shooting Star Pattern Indicator
'''
from v2.utils import findParams
from v2.strategy.indicators.param import Param
from v2.strategy.indicators.indicator import Indicator
from talib import CDLSHOOTINGSTAR as talib_CDLSHOOTINGSTAR

'''
CLASS: CDLSHOOTINGSTAR
WHAT:
    -> Implements the Shooting Star Pattern Indicator and adds the approprite columns to the dataset
    -> What is Shoting Star Pattern? --> https://hitandruncandlesticks.com/bullish-separating-lines-pattern/
    -> Params Required:
        -> 'N/A'
'''
class CDLSHOOTINGSTAR(Indicator):
    
    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: N/A
    RETURN:
        -> name of the column
    WHAT: 
        -> computes the Shooting Star Pattern
    TODO:
        -> This has not been tested
    '''
    def genData(self, dataset, gen_new_values=True):

        dataset[self.name] = talib_CDLSHOOTINGSTAR(dataset.open, dataset.high, dataset.low, dataset.close)

        return [self.name]
        
    def setDefaultParams(self):
        pass
