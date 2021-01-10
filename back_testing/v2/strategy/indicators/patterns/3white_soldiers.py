'''
FILE: cci.py
AUTHORS:
    -> Ross Copeland (rhcopeland101@gmail.com)
WHAT:
    -> This file contains the 3 White Soldiers Pattern Indicator
'''
from v2.utils import findParams
from v2.strategy.indicators.param import Param
from v2.strategy.indicators.indicator import Indicator
from v2.strategy.indicators.sma import SMA
import numpy as np
from talib import CDL3WHITESOLDIERS as talib_CDL3WHITESOLDIERS

'''
CLASS: CDL3WHITESOLDIERS
WHAT:
    -> Implements the 3 White Soldiers Pattern Indicator and adds the approprite columns to the dataset
    -> What is 3 White Soldiers Pattern? --> https://www.investopedia.com/terms/t/three_white_soldiers.asp
    -> Params Required:
        -> 'N/A'
'''
class CDL3WHITESOLDIERS(Indicator):
    
    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: N/A
    RETURN:
        -> name of the column
    WHAT: 
        -> computes the 3 White Soldiers Pattern Indicator
    TODO:
        -> This has not been tested
    '''
    def genData(self, dataset, gen_new_values=True):

        dataset[self.name] = talib_CDL3WHITESOLDIERS(dataset.open, dataset.high, dataset.low, dataset.close)

        return [self.name]
        
    def setDefaultParams(self):
        pass