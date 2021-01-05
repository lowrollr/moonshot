'''
FILE: stochastic_oscillator.py
AUTHORS:
    -> Jacob Marshall (marshingjay@gmail.com)
WHAT:
    -> This file contains the Stochastic Oscillator Indicator
'''

from v2.strategy.indicators.indicator import Indicator
from v2.utils import findParams
from v2.strategy.indicators.sma import SMA
from v2.strategy.indicators.param import Param
from talib import STOCH
import pandas

'''
CLASS: StochasticOscillator
WHAT:
    -> Calculates the stocastic oscillation and adds the approprite column to the dataset
    -> What is stochastic oscillator? --> https://www.investopedia.com/terms/s/stochasticoscillator.asp
    -> Params Required:
        -> 'highlow_range'
        -> 'k_period'
'''

class StochasticOscillator(Indicator):
    
    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: weather or not we should generate new values for each param belonging
            to this Indicator
        -> value (String) <optional>: dataframe column name to use for calculations
    RETURN:
        -> None
    WHAT: 
        -> calculates and adds the stochastic oscillation of the specified value over the given period to the dataset
    '''
    def genData(self, dataset, gen_new_values=True, value='close'):
        
        slowkperiod, fastkperiod, slowdperiod = findParams(self.params, ['slowkperiod', 'fastkperiod', 'slowdperiod'])
        if gen_new_values:
            slow_value = slowkperiod.genValue()
            fastkperiod.up = slow_value
            fastkperiod.genValue()
            slowdperiod.genValue()

        dataset['slowk' + self.appended_name], dataset['slowd' + self.appended_name] = STOCH(close=dataset['close'], high=dataset['high'], low=dataset['low'], slowk_period=slowkperiod.value, fastk_period=fastkperiod.value, slowd_period=slowdperiod.value)


    def setDefaultParams(self):
        self.params = [
            Param(5,10000,0,'slowkperiod',500),
            Param(5,10000,0,'slowdperiod',500),
            Param(5,10000,0,'fastkperiod',300)
        ]

        