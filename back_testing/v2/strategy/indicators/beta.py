'''
FILE: beta.py
AUTHORS:
    -> Ross Copeland (rhcopeland101@gmail.com)
WHAT:
    -> This file contains the beta Indicator
'''

import pandas
import numpy as np


from v2.strategy.indicators.param import Param
from v2.strategy.indicators.indicator import Indicator
from v2.utils import findParams

from talib import BETA as talib_BETA
'''
CLASS: Beta
WHAT:
    -> Calculates variance and adds the approprite column to the dataset
    -> What is beta? --> https://www.investopedia.com/investing/beta-know-risk/
    -> Params Required:
        -> 'period'
'''
class Beta(Indicator):

    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: weather or not we should generate new values for each param belonging
            to this Indicator
        -> value (String) <optional>: dataframe column name to use for calculations
    RETURN:
        -> None
    WHAT: 
        -> adds the beta of the specified value over the given period
    '''
    def genData(self, dataset, gen_new_values=True, value='close'):
        period = findParams(self.params, ['period'])[0]
        if gen_new_values:
            period.genValue()

        dataset[self.name] = talib_BETA(dataset.high, dataset.close, timeperiod=period.value)
        return [self.name]
    def setDefaultParams(self):
        self.params = [
            Param(5,10000,0,'period',400)
        ]