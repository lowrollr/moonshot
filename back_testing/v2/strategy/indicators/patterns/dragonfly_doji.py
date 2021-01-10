'''
FILE: dragonfly_doji.py
AUTHORS:
    -> Ross Copeland (rhcopeland101@gmail.com)
WHAT:
    -> This file contains the Dragonfly Doji Indicator
'''
from v2.utils import findParams
from v2.strategy.indicators.param import Param
from v2.strategy.indicators.indicator import Indicator
from talib import CDLDRAGONFLYDOJI as talib_CDLDRAGONFLYDOJI

'''
CLASS: CDLDRAGONFLYDOJI
WHAT:
    -> Implements the Dragonfly Doji Pattern Indicator and adds the approprite columns to the dataset
    -> What is Dragonfly Doji Pattern? --> https://www.investopedia.com/terms/d/dragonfly-doji.asp
    -> Params Required:
        -> 'N/A'
'''
class CDLDRAGONFLYDOJI(Indicator):
    
    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: N/A
    RETURN:
        -> name of the column
    WHAT: 
        -> computes the Dragonfly Doji Pattern
    TODO:
        -> This has not been tested
    '''
    def genData(self, dataset, gen_new_values=True):

        dataset[self.name] = talib_CDLDRAGONFLYDOJI(dataset.open, dataset.high, dataset.low, dataset.close)

        return [self.name]
        
    def setDefaultParams(self):
        pass
