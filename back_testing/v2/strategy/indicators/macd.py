'''
FILE: macd.py
AUTHORS:
    -> Jacob Marshall (marshingjay@gmail.com)
WHAT:
    -> This file contains the MACD Indicator
'''

from v2.strategy.indicators.indicator import Indicator
from v2.strategy.indicators.ema import EMA
from v2.utils import findParams
from v2.strategy.indicators.param import Param

from talib import MACD as talib_MACD

'''
CLASS: MACD
WHAT:
    -> Implements the MACD Indicator and adds the approprite columns to the dataset
    -> What is MACD? --> https://www.investopedia.com/trading/macd/
    -> Params Required:
        -> 'ema_slow'
        -> 'ema_fast'
        -> 'signal'
'''
class MACD(Indicator):
    
    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: weather or not we should generate new values for each param belonging
            to this Indicator
        -> value (String) <optional>: dataframe column name to use for calculations
    RETURN:
        -> None
    WHAT: 
        -> Adds columns with slow, fast, and signal EMAs
        -> Uses values from these columns to calculate MACD value
        -> the resultant value from the MACD calculation is placed in the 'macd_diff' column
    '''
    def genData(self, dataset, gen_new_values=True, value='close'):
        
        # params named 'ema_slow', 'ema_fast', and 'signal' must all be present
        ema_slow_param, ema_fast_param, signal_param = findParams(self.params, ['ema_slow', 'ema_fast', 'signal'])
        # generate new values for each param, if necessary
        if gen_new_values:
            ema_slow_value = ema_slow_param.genValue()
            # ema_fast value must be less than ema_slow, set the upper bound
            # before generating its value
            ema_fast_param.up = ema_slow_value
            ema_fast_value = ema_fast_param.genValue()
            # signal value must be less than ema_slow and greater than ema_fast
            # set bounds accordingly before generating value
            signal_param.up = ema_slow_value
            signal_param.low = ema_fast_value
            signal_param.genValue()

        dataset[self.name], dataset[self.name + '_signal'], dataset[self.name + '_hist'] = talib_MACD(dataset[value], slowperiod=ema_slow_param.value, fastperiod=ema_fast_param.value, signalperiod=signal_param.value)

        return [self.name, self.name + '_signal', self.name + '_hist']

    def setDefaultParams(self):
        self.params = [
            Param(5, 10000, 0,'ema_slow',400),
            Param(5, 10000, 0, 'ema_fast', 285),
            Param(5, 10000, 0, 'signal', 315)
        ]