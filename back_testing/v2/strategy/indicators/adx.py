'''
FILE: adx.py
AUTHORS:
    -> Jacob Marshall (marshingjay@gmail.com)
WHAT:
    -> This file contains the ADX Indicator
'''

import pandas
import numpy as np


from v2.strategy.indicators.param import Param
from v2.strategy.indicators.indicator import Indicator
from v2.utils import findParams

from talib import ADX as talib_ADX
'''
CLASS: ADX
WHAT:
    -> What is beta? --> https://www.investopedia.com/terms/a/adx.asp
    -> Params Required:
        -> 'period'
'''
class ADX(Indicator):

    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: weather or not we should generate new values for each param belonging
            to this Indicator
        -> value (String) <optional>: dataframe column name to use for calculations
    RETURN:
        -> None
    WHAT: 
        -> calculates ADX for the given period
    '''
    def genData(self, dataset, gen_new_values=True):
        period = findParams(self.params, ['period'])[0]
        if gen_new_values:
            period.genValue()

        dataset[self.name] = talib_ADX(dataset.high, dataset.low, dataset.close, timeperiod=period.value)
        return [self.name]

    def setDefaultParams(self):
        self.params = [
            Param(5,10000,0,'period',100)
        ]