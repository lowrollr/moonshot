'''
FILE: high_wave.py
AUTHORS:
    -> Ross Copeland (rhcopeland101@gmail.com)
WHAT:
    -> This file contains the High Wave Pattern Indicator
'''
from v2.utils import findParams
from v2.strategy.indicators.param import Param
from v2.strategy.indicators.indicator import Indicator
from talib import CDLHIGHWAVE as talib_CDLHIGHWAVE

'''
CLASS: CDLHARAMI
WHAT:
    -> Implements the High Wave Pattern Indicator and adds the approprite columns to the dataset
    -> What is Harami Cross Pattern? --> https://bullishbears.com/high-wave-candlesticks/
    -> Params Required:
        -> 'N/A'
'''
class CDLHIGHWAVE(Indicator):
    
    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: N/A
    RETURN:
        -> name of the column
    WHAT: 
        -> computes the High Wave Pattern Indicator
    TODO:
        -> This has not been tested
    '''
    def genData(self, dataset, gen_new_values=True):

        dataset[self.name] = talib_CDLHIGHWAVE(dataset.open, dataset.high, dataset.low, dataset.close)

        return [self.name]
        
    def setDefaultParams(self):
        pass
   




