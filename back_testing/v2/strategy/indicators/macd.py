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

        # add slow, fast EMAs to dataset
        ema_slow_param_simple = Param(_name='period', _default=ema_slow_param.value)
        ema_slow = EMA([ema_slow_param_simple], _name='ema_slow', _appended_name=self.appended_name)
        ema_slow.genData(dataset, gen_new_values=False, value=value)
        
        ema_fast_param_simple = Param(_name='period', _default=ema_fast_param.value)
        ema_fast = EMA([ema_fast_param_simple], _name='ema_fast', _appended_name=self.appended_name)
        ema_fast.genData(dataset, gen_new_values=False, value=value)

        # add fast - slow diff to dataset
        dataset['macd_diff_' + self.appended_name] = dataset['ema_fast'] - dataset['ema_slow']

        # compute signal EMA using fast - slow diff
        # note the value used is the data from the previously added column
        signal_param_simple = Param(_name='period', _default=signal_param.value)
        signal = EMA([signal_param_simple], _name='signal', _appended_name=self.appended_name)
        signal.genData(dataset, gen_new_values=False, value=value)

        # final macd calculation, now we are finished
        dataset[self.name] = dataset['macd_diff_' + self.appended_name] - dataset['signal']