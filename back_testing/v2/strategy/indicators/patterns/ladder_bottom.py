'''
FILE: ladder_bottom.py
AUTHORS:
    -> Ross Copeland (rhcopeland101@gmail.com)
WHAT:
    -> This file contains the Ladder Bottom Indicator
'''
from v2.utils import findParams
from v2.strategy.indicators.param import Param
from v2.strategy.indicators.indicator import Indicator
from talib import CDLLADDERBOTTOM as talib_CDLLADDERBOTTOM

'''
CLASS: CDLHIKKAKE
WHAT:
    -> Implements the Ladder Bottom Pattern Indicator and adds the approprite columns to the dataset
    -> What is Ladder Bottom Pattern? --> https://www.investopedia.com/terms/l/ladder-bottom.asp
    -> Params Required:
        -> 'N/A'
'''
class CDLLADDERBOTTOM(Indicator):
    
    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: N/A
    RETURN:
        -> name of the column
    WHAT: 
        -> computes the Ladder Bottom Pattern
    TODO:
        -> This has not been tested
    '''
    def genData(self, dataset, gen_new_values=True):

        dataset[self.name] = talib_CDLLADDERBOTTOM(dataset.open, dataset.high, dataset.low, dataset.close)

        return [self.name]
        
    def setDefaultParams(self):
        pass
