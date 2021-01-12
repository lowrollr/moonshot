'''
FILE: takuri.py
AUTHORS:
    -> Ross Copeland (rhcopeland101@gmail.com)
WHAT:
    -> This file contains the Takuri Pattern Indicator
'''
from v2.utils import findParams
from v2.strategy.indicators.param import Param
from v2.strategy.indicators.indicator import Indicator
from talib import CDLTAKURI as talib_CDLTAKURI

'''
CLASS: CDLTAKURI
WHAT:
    -> Implements the Takuri Pattern Indicator and adds the approprite columns to the dataset
    -> What is Takuri Pattern? --> https://patternswizard.com/takuri-candlestick-pattern/
    -> Params Required:
        -> 'N/A'
'''
class CDLTAKURI(Indicator):
    
    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: N/A
    RETURN:
        -> name of the column
    WHAT: 
        -> computes the Takuri Pattern
    TODO:
        -> This has not been tested
    '''
    def genData(self, dataset, gen_new_values=True):

        dataset[self.name] = talib_CDLTAKURI(dataset.open, dataset.high, dataset.low, dataset.close)

        return [self.name]
        
    def setDefaultParams(self):
        pass
