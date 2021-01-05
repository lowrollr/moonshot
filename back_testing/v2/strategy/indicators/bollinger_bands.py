'''
FILE: bollinger_bands.py
AUTHORS:
    -> Jacob Marshall (marshingjay@gmail.com)
WHAT:
    -> This file contains the Bollinger Band Indicator
'''
from v2.strategy.indicators.indicator import Indicator
from v2.utils import findParams
from v2.strategy.indicators.sma import SMA
from talib import BBANDS
import pandas

'''
CLASS: EMA
WHAT:
    -> Implements the Bollinger Bands Indicator and adds the approprite columns to the dataset
    -> What are Bollinger Bands? --> 
    -> Params Required:
        -> 'period'
'''

class BollingerBands(Indicator):
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
        dev_down, dev_up, period = findParams(self.params, ['nbdevup', 'nbdevdn', 'period'])
        
        if gen_new_values:
            if dev_down and dev_up:
                dev_down.genValue()
                dev_up.genValue()
            period.genValue()
        if dev_down and dev_up:
            dataset['boll_upper' + self.appended_name], dataset['boll_middle' + self.appended_name], dataset['boll_lower' + self.appended_name] = BBANDS(dataset[value], timeperiod=period.value, nbdevup=dev_up.value, nbdevdown=dev_down.value)
        else:
            dataset['boll_upper' + self.appended_name], dataset['boll_middle' + self.appended_name], dataset['boll_lower' + self.appended_name] = BBANDS(dataset[value], timeperiod=period.value)

        