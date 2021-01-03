'''
FILE: ema.py
AUTHORS:
    -> Jacob Marshall (marshingjay@gmail.com)
WHAT:
    -> This file contains the EMA (Exponential Moving Average) Indicator
'''

import pandas

from v2.utils import findParams
from v2.strategy.indicators.indicator import Indicator
from talib import EMA as talib_EMA

'''
CLASS: EMA
WHAT:
    -> Implements the EMA Indicator and adds the approprite columns to the dataset
    -> What is EMA? --> https://www.investopedia.com/terms/e/ema.asp
    -> Params Required:
        -> 'period'
'''
class EMA(Indicator):
    
    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: weather or not we should generate new values for each param belonging
            to this Indicator
        -> value (String) <optional>: dataframe column name to use for calculations
    RETURN:
        -> None
    WHAT: 
        -> computes the exponential moving average of the specified value over the given period
    '''
    def genData(self, dataset, gen_new_values=True, value='close'):

        # param named 'period' must be present
        period = findParams(self.params, ['period'])[0]
        # generate a new period value, if necessary
        if gen_new_values:
            period.genValue()

        # # compute EMA and add to the dataset
        # dataset[self.name] = dataset[value].ewm(span=period.value, adjust=False).mean()
        
        dataset[self.name] = talib_EMA(dataset[value], timeperiod=period.value)