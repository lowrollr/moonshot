'''
FILE: willr.py
AUTHORS:
    -> Ross Copeland (rcopeland101@gmail.com)
WHAT:
    -> This file contains the Williams' %R
'''
from v2.strategy.indicators.indicator import Indicator
from v2.strategy.indicators.param import Param
from v2.utils import findParams
import pandas as pd

from talib import WILLR as talib_WILLR

'''
CLASS: WILLR
WHAT:
    -> Calculates the Williams' %R and adds the approprite column to the dataset
    -> What is Williams' %R? --> https://pythonforfinance.net/2019/06/26/ichimoku-trading-strategy-with-python/
    -> Params Required:
        -> None
'''

class WILLR(Indicator):
    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: weather or not we should generate new values for each param belonging
            to this Indicator
        -> value (String) <optional>: dataframe column name to use for calculations
    RETURN:
        -> None
    WHAT: 
        -> calculates and adds the Ichimoku Cloud values of the specified value to the dataset
    '''
    def genData(self, dataset, gen_new_values=True):
        period = findParams(self.params, ['period'])[0]
        
        if gen_new_values:
            period.genValue()

        dataset[self.name] = talib_WILLR(dataset.high, dataset.low, dataset.close, timeperiod=period.value)

        return [self.name]

    def setDefaultParams(self):
        self.params = [
            Param(5, 10000, 0,'period', 300)
        ]