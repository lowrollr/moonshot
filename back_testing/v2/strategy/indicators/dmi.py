'''
FILE: dmi.py
AUTHORS:
    -> Ross Copeland (marshingjay@gmail.com)
WHAT:
    -> This file contains the DMI (Directional Movement Index) Indicator
'''

import pandas

from v2.strategy.indicators.param import Param
from v2.utils import findParams
from v2.strategy.indicators.indicator import Indicator
from talib import DX as talib_DMI

'''
CLASS: DMI
WHAT:
    -> Implements the DMI Indicator and adds the approprite columns to the dataset
    -> What is DMI? --> https://www.investopedia.com/terms/d/dmi.asp
    -> Params Required:
        -> 'period'
'''
class DMI(Indicator):
    
    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: weather or not we should generate new values for each param belonging
            to this Indicator
        -> value (String) <optional>: dataframe column name to use for calculations
    RETURN:
        -> None
    WHAT: 
        -> computes the directional movement index of the specified value over the given period
    '''
    def genData(self, dataset, gen_new_values=True):

        # param named 'period' must be present
        period = findParams(self.params, ['period'])[0]
        # generate a new period value, if necessary
        if gen_new_values:
            period.genValue()
        
        dataset[self.name] = talib_DMI(dataset.high, dataset.low, dataset.close, timeperiod=period.value)

        return [self.name]

    def setDefaultParams(self):
        self.params = [
            Param(5,10000,0,'period',50)
        ]