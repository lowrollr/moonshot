'''
FILE: gravestone_doji.py
AUTHORS:
    -> Ross Copeland (rhcopeland101@gmail.com)
WHAT:
    -> This file contains the Gravestone Doji Indicator
'''
from v2.utils import findParams
from v2.strategy.indicators.param import Param
from v2.strategy.indicators.indicator import Indicator
from talib import CDLGRAVESTONEDOJI as talib_CDLGRAVESTONEDOJI

'''
CLASS: CDLGRAVESTONEDOJI
WHAT:
    -> Implements the Gravestone Doji Pattern Indicator and adds the approprite columns to the dataset
    -> What is Gravestone Doji Pattern? --> https://www.investopedia.com/terms/g/gravestone-doji.asp
    -> Params Required:
        -> 'N/A'
'''
class CDLGRAVESTONEDOJI(Indicator):
    
    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: N/A
    RETURN:
        -> name of the column
    WHAT: 
        -> computes the Gravestone Doji Pattern
    TODO:
        -> This has not been tested
    '''
    def genData(self, dataset, gen_new_values=True):

        dataset[self.name] = talib_CDLGRAVESTONEDOJI(dataset.open, dataset.high, dataset.low, dataset.close)

        return [self.name]
        
    def setDefaultParams(self):
        pass
