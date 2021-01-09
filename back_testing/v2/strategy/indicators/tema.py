'''
FILE: tema.py
AUTHORS:
    -> Ross Copeland (rhcopeland101@gmail.com)
WHAT:
    -> This file contains the TEMA (Triple Exponential Moving Average) Indicator
'''
from v2.utils import findParams
from v2.strategy.indicators.param import Param
from v2.strategy.indicators.indicator import Indicator
from v2.strategy.indicators.ema import EMA
import numpy as np
from talib import TEMA as talib_TEMA

'''
CLASS: TEMA
WHAT:
    -> Implements the TEMA Indicator and adds the approprite columns to the dataset
    -> What is TEMA? --> https://www.investopedia.com/terms/t/triple-exponential-moving-average.asp
    -> Params Required:
        -> 'period'
'''
class TEMA(Indicator):
    
    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: weather or not we should generate new values for each param belonging
            to this Indicator
        -> value (String) <optional>: dataframe column name to use for calculations
    RETURN:
        -> None
    WHAT: 
        -> computes the triple exponential moving average of the specified value over the given period
        -> Formula: TEMA = (3*EMA - 3*EMA(EMA)) + EMA(EMA(EMA))
    TODO:
        -> This has not been tested
    '''
    def genData(self, dataset, gen_new_values=True):

        # param named 'period' must be present
        period = findParams(self.params, ['period'])[0]
        # generate a new period value, if necessary
        if gen_new_values:
            period.genValue()
        
        dataset[self.name] = talib_TEMA(dataset[self.value], timeperiod=period.value)

        return [self.name]

    def setDefaultParams(self):
        self.params = [
            Param(5,10000,0,'period', 10)
        ]