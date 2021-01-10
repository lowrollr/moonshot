'''
FILE: rickshaw_man.py
AUTHORS:
    -> Ross Copeland (rhcopeland101@gmail.com)
WHAT:
    -> This file contains the Rickshaw Man Pattern Indicator
'''
from v2.utils import findParams
from v2.strategy.indicators.param import Param
from v2.strategy.indicators.indicator import Indicator
from talib import CDLRICKSHAWMAN as talib_CDLRICKSHAWMAN

'''
CLASS: CDLRICKSHAWMAN
WHAT:
    -> Implements the Richshaw Man Pattern Indicator and adds the approprite columns to the dataset
    -> What is Rickshaw Man Pattern? --> https://www.investopedia.com/terms/r/rickshaw-man.asp
    -> Params Required:
        -> 'N/A'
'''
class CDLRICKSHAWMAN(Indicator):
    
    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: N/A
    RETURN:
        -> name of the column
    WHAT: 
        -> computes the Rickshaw Man Pattern
    TODO:
        -> This has not been tested
    '''
    def genData(self, dataset, gen_new_values=True):

        dataset[self.name] = talib_CDLRICKSHAWMAN(dataset.open, dataset.high, dataset.low, dataset.close)

        return [self.name]
        
    def setDefaultParams(self):
        pass
