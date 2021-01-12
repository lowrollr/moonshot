'''
FILE: on_neck.py
AUTHORS:
    -> Ross Copeland (rhcopeland101@gmail.com)
WHAT:
    -> This file contains the On Neck Indicator
'''
from v2.utils import findParams
from v2.strategy.indicators.param import Param
from v2.strategy.indicators.indicator import Indicator
from talib import CDLONNECK as talib_CDLONNECK

'''
CLASS: CDLONNECK
WHAT:
    -> Implements the On Neck Pattern Indicator and adds the approprite columns to the dataset
    -> What is On Neck Pattern? --> https://hitandruncandlesticks.com/on-neck-candlestick-pattern/
    -> Params Required:
        -> 'N/A'
'''
class CDLONNECK(Indicator):
    
    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: N/A
    RETURN:
        -> name of the column
    WHAT: 
        -> computes the On Neck Pattern
    TODO:
        -> This has not been tested
    '''
    def genData(self, dataset, gen_new_values=True):

        dataset[self.name] = talib_CDLONNECK(dataset.open, dataset.high, dataset.low, dataset.close)

        return [self.name]
        
    def setDefaultParams(self):
        pass
