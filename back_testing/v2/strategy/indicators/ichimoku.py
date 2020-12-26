'''
FILE: ichimoku.py
AUTHORS:
    -> Ross Copeland (rcopeland101@gmail.com)
WHAT:
    -> This file contains the Ichimoku Cloud Indicator
'''
from v2.strategy.indicators.indicator import Indicator
from v2.utils import findParams
import pandas as pd

'''
CLASS: Ichimoku
WHAT:
    -> Calculates the Ichimoku Cloud and adds the approprite column to the dataset
    -> What is Ichimoku Cloud? --> https://pythonforfinance.net/2019/06/26/ichimoku-trading-strategy-with-python/
    -> Params Required:
        -> None
TODO:
    -> make the number of minutes rolling
'''

class Ichimoku(Indicator):
    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: weather or not we should generate new values for each param belonging
            to this Indicator
        -> value (String) <optional>: dataframe column name to use for calculations
    RETURN:
        -> None
    WHAT: 
        -> calculates and adds the Ichimoku Cloud values of the specified value to the dataset
    '''
    def genData(self, dataset, gen_new_values=True, value='close'):
        #standard vals are short_window = 9, medium_window = 26, long_window = 52
        short_window, medium_window, long_window = findParams(self.params, ['short_window', 'medium_window', 'long_window'])
        short_period_high = dataset['high'].rolling(window=short_window).max()
        short_period_low = dataset['low'].rolling(window=short_window).min()
        dataset["tenkan_sen" + self.appended_name] = (short_period_high + short_period_low) / 2

        medium_period_high = dataset['high'].rolling(window=medium_window).max()
        medium_period_low = dataset['low'].rolling(window=medium_window).min()
        dataset['kijun_sen' + self.appended_name] = (medium_period_high + medium_period_low) / 2

        dataset["senkou_span_a" + self.appended_name] = ((dataset["tenkan_sen"] + dataset["kijun_sen"]) / 2).shift(medium_window)

        long_period_high = dataset['high'].rolling(window=long_window).max()
        long_period_low = dataset['low'].rolling(window=long_window).min()
        dataset["senkou_span_b" + self.appended_name] = ((long_period_high + long_period_low) / 2).shift(medium_window)

        dataset.dropna()