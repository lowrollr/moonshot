'''
FILE: cci.py
AUTHORS:
    -> Ross Copeland (rhcopeland101@gmail.com)
WHAT:
    -> This file contains the 3 Line Strike Pattern Indicator
'''
from v2.utils import findParams
from v2.strategy.indicators.param import Param
from v2.strategy.indicators.indicator import Indicator
from talib import CDL3LINESTRIKE as talib_CDL3LINESTRIKE

'''
CLASS: CDL3LINESTRIKE
WHAT:
    -> Implements the 3 Line Strike Pattern Indicator and adds the approprite columns to the dataset
    -> What is 3 Line Strike Pattern? --> https://forexop.com/candlesticks/three-line-strike/
    -> Params Required:
        -> 'N/A'
'''
class CDL3LINESTRIKE(Indicator):
    
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

        dataset[self.name] = talib_CDL3LINESTRIKE(dataset.open, dataset.high, dataset.low, dataset.close)

        return [self.name]
        
    def setDefaultParams(self):
        pass