'''
FILE: cmo.py
AUTHORS:
    -> Ross Copeland (rhcopeland101@gmail.com)
WHAT:
    -> This file contains the NATR (Normalized Average True Range) Indicator
'''
from v2.utils import findParams
from v2.strategy.indicators.param import Param
from v2.strategy.indicators.indicator import Indicator
from v2.strategy.indicators.sma import SMA
import numpy as np
from talib import NATR as talib_NATR

'''
CLASS: NATR
WHAT:
    -> Implements the NATR Indicator and adds the approprite columns to the dataset
    -> Indicator to measure the volatility of the asset
    -> What is NATR? --> https://tulipindicators.org/natr
    -> Params Required:
        -> 'period'
'''
class NATR(Indicator):
    
    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: weather or not we should generate new values for each param belonging
            to this Indicator
        -> value (String) <optional>: dataframe column name to use for calculations
    RETURN:
        -> None
    WHAT: 
        -> computes the NATR of the specified value over the given period
    TODO:
        -> This has not been tested
    '''
    def genData(self, dataset, gen_new_values=True, value='close'):

        # param named 'period' must be present
        period = findParams(self.params, ['period'])[0]
        # generate a new period value, if necessary
        if gen_new_values:
            period.genValue()
        
        dataset[self.name] = talib_NATR(dataset.high, dataset.low, dataset.close, timeperiod=period.value)