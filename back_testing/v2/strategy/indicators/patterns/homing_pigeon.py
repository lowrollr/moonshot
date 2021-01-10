'''
FILE: homing_pigeon.py
AUTHORS:
    -> Ross Copeland (rhcopeland101@gmail.com)
WHAT:
    -> This file contains the Homing Pigeon Pattern Indicator
'''
from v2.utils import findParams
from v2.strategy.indicators.param import Param
from v2.strategy.indicators.indicator import Indicator
from talib import CDLHOMINGPIGEON as talib_CDLHOMINGPIGEON

'''
CLASS: CDLHIKKAKE
WHAT:
    -> Implements the Homing Pigeon Pattern Indicator and adds the approprite columns to the dataset
    -> What is Homing Pigeon Pattern? --> https://www.investopedia.com/terms/b/bullishhomingpigeon.asp
    -> Params Required:
        -> 'N/A'
'''
class CDLHOMINGPIGEON(Indicator):
    
    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: N/A
    RETURN:
        -> name of the column
    WHAT: 
        -> computes the Homing Pigeon Pattern
    TODO:
        -> This has not been tested
    '''
    def genData(self, dataset, gen_new_values=True):

        dataset[self.name] = talib_CDLHOMINGPIGEON(dataset.open, dataset.high, dataset.low, dataset.close)

        return [self.name]
        
    def setDefaultParams(self):
        pass
