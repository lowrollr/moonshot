'''
FILE: cmo.py
AUTHORS:
    -> Ross Copeland (rhcopeland101@gmail.com)
WHAT:
    -> This file contains the CMO (Chande Momentum Oscilator) Indicator
'''
from v2.utils import findParams
from v2.strategy.indicators.param import Param
from v2.strategy.indicators.indicator import Indicator
from v2.strategy.indicators.sma import SMA
import numpy as np
from talib import CMO as talib_CMO

'''
CLASS: CMO
WHAT:
    -> Implements the CMO Indicator and adds the approprite columns to the dataset
    -> What is CMO? --> https://www.investopedia.com/terms/c/commoditychannelindex.asp
    -> Params Required:
        -> 'period'
'''
class CMO(Indicator):
    
    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: weather or not we should generate new values for each param belonging
            to this Indicator
        -> value (String) <optional>: dataframe column name to use for calculations
    RETURN:
        -> None
    WHAT: 
        -> computes the CMO of the specified value over the given period
    TODO:
        -> This has not been tested
    '''
    def genData(self, dataset, gen_new_values=True):

        # param named 'period' must be present
        period = findParams(self.params, ['period'])[0]
        # generate a new period value, if necessary
        if gen_new_values:
            period.genValue()
        
        dataset[self.name] = talib_CMO(dataset[self.value], timeperiod=period.value)

        return [self.name]
        
    def setDefaultParams(self):
        self.params = [
            Param(5,10000,0,'period',400)
        ]