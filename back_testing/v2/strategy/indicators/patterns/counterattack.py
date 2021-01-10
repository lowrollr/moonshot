'''
FILE: counterattack.py
AUTHORS:
    -> Ross Copeland (rhcopeland101@gmail.com)
WHAT:
    -> This file contains the Counterattack Indicator
'''
from v2.utils import findParams
from v2.strategy.indicators.param import Param
from v2.strategy.indicators.indicator import Indicator
from talib import CDLCOUNTERATTACK as talib_CDLCOUNTERATTACK

'''
CLASS: CDLCOUNTERATTACK
WHAT:
    -> Implements the Counterattack Pattern Indicator and adds the approprite columns to the dataset
    -> What is Counterattack Pattern? --> https://www.investopedia.com/terms/c/counterattack.asp
    -> Params Required:
        -> 'N/A'
'''
class CDLCOUNTERATTACK(Indicator):
    
    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: N/A
    RETURN:
        -> name of the column
    WHAT: 
        -> computes the Counterattack Pattern
    TODO:
        -> This has not been tested
    '''
    def genData(self, dataset, gen_new_values=True):

        dataset[self.name] = talib_CDLCOUNTERATTACK(dataset.open, dataset.high, dataset.low, dataset.close)

        return [self.name]
        
    def setDefaultParams(self):
        pass
