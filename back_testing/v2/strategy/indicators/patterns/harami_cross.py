'''
FILE: harami_cross.py
AUTHORS:
    -> Ross Copeland (rhcopeland101@gmail.com)
WHAT:
    -> This file contains the Harami Cross Pattern Indicator
'''
from v2.utils import findParams
from v2.strategy.indicators.param import Param
from v2.strategy.indicators.indicator import Indicator
from talib import CDLHARAMICROSS as talib_CDLHARAMICROSS

'''
CLASS: CDLHARAMI
WHAT:
    -> Implements the Harami Cross Pattern Indicator and adds the approprite columns to the dataset
    -> What is Harami Cross Pattern? --> https://www.investopedia.com/terms/h/haramicross.asp
    -> Params Required:
        -> 'N/A'
'''
class CDLHARAMICROSS(Indicator):
    
    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: N/A
    RETURN:
        -> name of the column
    WHAT: 
        -> computes the Harami Cross Pattern Indicator
    TODO:
        -> This has not been tested
    '''
    def genData(self, dataset, gen_new_values=True):

        dataset[self.name] = talib_CDLHARAMICROSS(dataset.open, dataset.high, dataset.low, dataset.close)

        return [self.name]
        
    def setDefaultParams(self):
        pass
   




