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
        
        param_highlow_range, param_k_period_sma = findParams(self.params, ['highlow_range', 'k_period'])
        if gen_new_values:
            highlow_range_value = param_highlow_range.genValue()
            param_k_period_sma.up = highlow_range_value

        dataset['stosc_high_price'] = dataset['low'].rolling(window=int(param_highlow_range.value)).min()
        dataset['stosc_low_price'] = dataset['high'].rolling(window=int(param_highlow_range.value)).max()
        dataset['stosc_k'] = 100*((dataset['close'] - dataset['stosc_low_price']) / (dataset['stosc_high_price'] - dataset['stosc_low_price']))

        k_period_sma = SMA([param_k_period_sma], _name='stosc_d')
        k_period_sma.genData(dataset, gen_new_values=gen_new_values, value='stosc_k')