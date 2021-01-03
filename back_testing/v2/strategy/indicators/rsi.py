'''
FILE: rsi.py
AUTHORS:
    -> Jacob Marshall (marshingjay@gmail.com)
WHAT:
    -> This file contains the RSI Indicator
'''

import pandas

from v2.strategy.indicators.indicator import Indicator
from v2.utils import findParams
from v2.strategy.indicators.smma import SMMA

from talib import RSI as talib_RSI

'''
CLASS: RSI
WHAT:
    -> Implements the RSI Indicator and adds the approprite columns to the dataset
    -> What is RSI? --> https://www.investopedia.com/terms/r/rsi.asp
    -> Params Required:
        -> 'period'
'''
class RSI(Indicator):
    
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

        # param named 'period' must be present
        period = findParams(self.params, ['period'])[0]
        # generate a new period value, if necessary
        if gen_new_values:
            period.genValue()

        # # compute diff for selected value i.e. close
        # dataset['rsi_diff' + self.appended_name] =  dataset[value].diff()

        # # compute rsi_u and rsi_d 
        # dataset['rsi_u' + self.appended_name] = (abs(dataset['rsi_diff']) + dataset['rsi_diff']) / 2
        # dataset['rsi_d' + self.appended_name] = (abs(dataset['rsi_diff']) - dataset['rsi_diff']) / 2

        # # compute smma for rsi_u and rsi_d
        # smma_u = SMMA([period], _name='rsi_smma_u', _appended_name=self.appended_name)
        # smma_d = SMMA([period], _name='rsi_smma_d', _appended_name=self.appended_name)
        # smma_u.genData(dataset, gen_new_values=False, value='rsi_u')
        # smma_d.genData(dataset, gen_new_values=False, value='rsi_d')

        # # compute RSI
        # dataset[self.name] = 100 - (100 / (1 + (dataset['rsi_smma_u'] / dataset['rsi_smma_d'])))

        # # clean up intermediate columns
        # dataset.drop(['rsi_u' + self.appended_name, 'rsi_d' + self.appended_name, 'rsi_diff' + self.appended_name,\
        # 'rsi_smma_u' + self.appended_name, 'rsi_smma_d' + self.appended_name], axis=1, inplace=True)

        dataset[self.name] = talib_RSI(dataset[value], timeperiod=period.value)