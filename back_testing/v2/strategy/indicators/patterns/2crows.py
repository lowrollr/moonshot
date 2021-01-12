'''
FILE: 2crows.py
AUTHORS:
    -> Ross Copeland (rhcopeland101@gmail.com)
WHAT:
    -> This file contains the 2 Crow Pattern Indicator
'''
from v2.utils import findParams
from v2.strategy.indicators.param import Param
from v2.strategy.indicators.indicator import Indicator
from talib import CDL2CROWS as talib_CDL2CROWS

'''
CLASS: CDL2CROWS
WHAT:
    -> Implements the 2 Crow Pattern Indicator and adds the approprite columns to the dataset
    -> What is 2 Crow Pattern? --> https://www.candlescanner.com/candlestick-patterns/two-crows/
    -> Params Required:
        -> 'N/A'
'''
class CDL2CROWS(Indicator):
    
    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: N/A
    RETURN:
        -> name of the column
    WHAT: 
        -> computes the 2 Crow Pattern Indicator
    TODO:
        -> This has not been tested
    '''
    def genData(self, dataset, gen_new_values=True):

        dataset[self.name] = talib_CDL2CROWS(dataset.open, dataset.high, dataset.low, dataset.close)

        return [self.name]
        
    def setDefaultParams(self):
        pass