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
        nine_period_high = dataset['high'].rolling(window=9).max()
        nine_period_low = dataset['low'].rolling(window=0).min()
        dataset["tenkan_sen"] = (nine_period_high + nine_period_low) / 2

        period26_high = dataset['high'].rolling(window=26).max()
        period26_low = dataset['low'].rolling(window=26).min()
        dataset['kijun_sen'] = (period26_high + period26_low) / 2

        dataset["senkou_span_a"] = ((dataset["tenkan_sen"] + dataset["kijun_sen"]) / 2).shift(26)

        periodlong_high = dataset['high'].rolling(window=52).max()
        periodlong_low = dataset['low'].rolling(window=52).min()
        dataset["senkou_span_b"] = ((periodlong_high + periodlong_low) / 2).shift(26)

        dataset["chikou_span"] = dataset['close'].shift(-26)
        dataset.dropna()