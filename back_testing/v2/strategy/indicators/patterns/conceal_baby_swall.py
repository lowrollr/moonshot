'''
FILE: conceal_baby_swall.py
AUTHORS:
    -> Ross Copeland (rhcopeland101@gmail.com)
WHAT:
    -> This file contains the Conceal Baby Swallow Indicator
'''
from v2.utils import findParams
from v2.strategy.indicators.param import Param
from v2.strategy.indicators.indicator import Indicator
from talib import CDLCONCEALBABYSWALL as talib_CDLCONCEALBABYSWALL

'''
CLASS: CDLCONCEALBABYSWALL
WHAT:
    -> Implements the Conceal Baby Swallow Pattern Indicator and adds the approprite columns to the dataset
    -> What is Conceal Baby Swallow Pattern? --> https://tradingsim.com/blog/concealing-baby-swallow/
    -> Params Required:
        -> 'N/A'
'''
class CDLCONCEALBABYSWALL(Indicator):
    
    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: N/A
    RETURN:
        -> name of the column
    WHAT: 
        -> computes the Conceal Baby Swallow Pattern
    TODO:
        -> This has not been tested
    '''
    def genData(self, dataset, gen_new_values=True):

        dataset[self.name] = talib_CDLCONCEALBABYSWALL(dataset.open, dataset.high, dataset.low, dataset.close)

        return [self.name]
        
    def setDefaultParams(self):
        pass
