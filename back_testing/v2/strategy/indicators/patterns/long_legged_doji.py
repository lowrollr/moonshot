'''
FILE: long_legged_doji.py
AUTHORS:
    -> Ross Copeland (rhcopeland101@gmail.com)
WHAT:
    -> This file contains the Long Legged Doji Indicator
'''
from v2.utils import findParams
from v2.strategy.indicators.param import Param
from v2.strategy.indicators.indicator import Indicator
from talib import CDLLONGLEGGEDDOJI as talib_CDLLONGLEGGEDDOJI

'''
CLASS: CDLLONGLEGGEDDOJI
WHAT:
    -> Implements the Long Legged Doji Pattern Indicator and adds the approprite columns to the dataset
    -> What is Long Legged Doji Pattern? --> https://www.investopedia.com/terms/l/long-legged-doji.asp
    -> Params Required:
        -> 'N/A'
'''
class CDLLONGLEGGEDDOJI(Indicator):
    
    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: N/A
    RETURN:
        -> name of the column
    WHAT: 
        -> computes the Long Legged Doji Pattern
    TODO:
        -> This has not been tested
    '''
    def genData(self, dataset, gen_new_values=True):

        dataset[self.name] = talib_CDLLONGLEGGEDDOJI(dataset.open, dataset.high, dataset.low, dataset.close)

        return [self.name]
        
    def setDefaultParams(self):
        pass
