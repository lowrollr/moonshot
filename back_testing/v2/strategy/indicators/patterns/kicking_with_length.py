'''
FILE: kicking_with_length.py
AUTHORS:
    -> Ross Copeland (rhcopeland101@gmail.com)
WHAT:
    -> This file contains the Kicking With Length Pattern Indicator
'''
from v2.utils import findParams
from v2.strategy.indicators.param import Param
from v2.strategy.indicators.indicator import Indicator
from talib import CDLKICKINGBYLENGTH as talib_CDLKICKINGBYLENGTH

'''
CLASS: CDLHIKKAKE
WHAT:
    -> Implements the Kicking With Length Pattern Indicator and adds the approprite columns to the dataset
    -> What is Kicking With Length Pattern? --> ? https://hitandruncandlesticks.com/bullish-kicker-candlestick-pattern/
    -> Params Required:
        -> 'N/A'
'''
class CDLKICKINGBYLENGTH(Indicator):
    
    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: N/A
    RETURN:
        -> name of the column
    WHAT: 
        -> computes the Kicking With Length Pattern
    TODO:
        -> This has not been tested
    '''
    def genData(self, dataset, gen_new_values=True):

        dataset[self.name] = talib_CDLKICKINGBYLENGTH(dataset.open, dataset.high, dataset.low, dataset.close)

        return [self.name]
        
    def setDefaultParams(self):
        pass
