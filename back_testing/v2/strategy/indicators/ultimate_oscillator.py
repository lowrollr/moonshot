'''
FILE: ultimate_oscillator.py
AUTHORS:
    -> Jacob Marshall (marshingjay@gmail.com)
WHAT:
    -> This file contains the Ultimate Oscillator Indicator
'''
from v2.strategy.indicators.indicator import Indicator
from v2.strategy.indicators.param import Param
from v2.utils import findParams
from v2.strategy.indicators.sma import SMA
from talib import ULTOSC

'''
CLASS: UltimateOscillator
WHAT:
    -> Implements the Ultimate Oscillator Indicator and adds the approprite columns to the dataset
    -> What is the Ultimate Oscillator? --> 
    -> Params Required:
        -> 'period'
'''

class UltimateOscillator(Indicator):
    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: weather or not we should generate new values for each param belonging
            to this Indicator
        -> value (String) <optional>: dataframe column name to use for calculations
    RETURN:
        -> None
    WHAT: 
        -> calculates and adds the Bollinger Bands of the specified value over the given period to the dataset
    '''
    def genData(self, dataset, gen_new_values=True, value='close'):
        period1, period2, period3 = findParams(self.params, ['period1', 'period2', 'period3'])
        
        if gen_new_values:
            period1.genValue()
            period2.genValue()
            period3.genValue()

        dataset[self.name] = ULTOSC(high=dataset['high'], low=dataset['low'], close=dataset['close'], period1=period1.value, period2=period2.value, period3=period3.value)

        return [self.name]

    def setDefaultParams(self):
        self.params = [
            Param(5,10000,0,'period1',300),
            Param(5,10000,0,'period2',400),
            Param(5,10000,0,'period3',500)
            
        ]