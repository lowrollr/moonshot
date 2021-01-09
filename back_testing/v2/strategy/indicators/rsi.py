'''
FILE: rsi.py
AUTHORS:
    -> Jacob Marshall (marshingjay@gmail.com)
WHAT:
    -> This file contains the RSI Indicator
'''

import pandas

from v2.strategy.indicators.indicator import Indicator
from v2.strategy.indicators.param import Param
from v2.utils import findParams
from v2.strategy.indicators.smma import SMMA

from talib import RSI as talib_RSI

'''
CLASS: RSI
WHAT:
    -> Implements the RSI Indicator and adds the approprite columns to the dataset
    -> What is RSI? --> https://www.investopedia.com/terms/r/rsi.asp
    -> Params Required:
        -> 'period'
'''
class RSI(Indicator):
    
    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: weather or not we should generate new values for each param belonging
            to this Indicator
        -> value (String) <optional>: dataframe column name to use for calculations
    RETURN:
        -> None
    WHAT: 
        -> Adds columns with slow, fast, and signal EMAs
        -> Uses values from these columns to calculate MACD value
        -> the resultant value from the MACD calculation is placed in the 'macd_diff' column
    '''
    def genData(self, dataset, gen_new_values=True):

        # param named 'period' must be present
        period = findParams(self.params, ['period'])[0]
        # generate a new period value, if necessary
        if gen_new_values:
            period.genValue()

        dataset[self.name] = talib_RSI(dataset[self.value], timeperiod=period.value)


        return [self.name]

    def setDefaultParams(self):
        self.params = [
            Param(5,10000,0,'period', 60)
        ]