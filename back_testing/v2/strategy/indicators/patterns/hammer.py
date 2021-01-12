'''
FILE: hammer.py
AUTHORS:
    -> Ross Copeland (rhcopeland101@gmail.com)
WHAT:
    -> This file contains the Hammer Pattern Indicator
'''
from v2.utils import findParams
from v2.strategy.indicators.param import Param
from v2.strategy.indicators.indicator import Indicator
from talib import CDLHAMMER as talib_CDLHAMMER

'''
CLASS: CDLHAMMER
WHAT:
    -> Implements the Hammer Pattern Indicator and adds the approprite columns to the dataset
    -> What is Hammer Pattern? --> https://www.investopedia.com/terms/h/hammer.asp
    -> Params Required:
        -> 'N/A'
'''
class CDLHAMMER(Indicator):
    
    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: N/A
    RETURN:
        -> name of the column
    WHAT: 
        -> computes the Hammer Pattern Indicator
    TODO:
        -> This has not been tested
    '''
    def genData(self, dataset, gen_new_values=True):

        dataset[self.name] = talib_CDLHAMMER(dataset.open, dataset.high, dataset.low, dataset.close)

        return [self.name]
        
    def setDefaultParams(self):
        pass
   