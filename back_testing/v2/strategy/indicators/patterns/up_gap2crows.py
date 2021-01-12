'''
FILE: up_gap2crows.py
AUTHORS:
    -> Ross Copeland (rhcopeland101@gmail.com)
WHAT:
    -> This file contains the Upside Gap 2 Crows Pattern Indicator
'''
from v2.utils import findParams
from v2.strategy.indicators.param import Param
from v2.strategy.indicators.indicator import Indicator
from talib import CDLUPSIDEGAP2CROWS as talib_CDLUPSIDEGAP2CROWS

'''
CLASS: CDLUPSIDEGAP2CROWS
WHAT:
    -> Implements the Upside Gap 2 Crows Pattern Indicator and adds the approprite columns to the dataset
    -> What is Upside Gap 2 Crows Pattern? --> https://www.investopedia.com/terms/u/upside-gap-two-crows.asp
    -> Params Required:
        -> 'N/A'
'''
class CDLUPSIDEGAP2CROWS(Indicator):
    
    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: N/A
    RETURN:
        -> name of the column
    WHAT: 
        -> computes the Upside Gap 2 Crows Pattern
    TODO:
        -> This has not been tested
    '''
    def genData(self, dataset, gen_new_values=True):

        dataset[self.name] = talib_CDLUPSIDEGAP2CROWS(dataset.open, dataset.high, dataset.low, dataset.close)

        return [self.name]
        
    def setDefaultParams(self):
        pass
