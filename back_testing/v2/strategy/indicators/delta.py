'''
FILE: delta.py
AUTHORS:
    -> Jacob Marshall (marshingjay@gmail.com)
WHAT:
    -> This file contains the Delta Indicator
'''
import numpy as np
import pandas as pd
from v2.strategy.indicators.indicator import Indicator
from v2.utils import findParams
import pandas


'''
CLASS: Delta
WHAT:
    -> Calculates the delta for the given window and adds the approprite column to the dataset
    -> What is delta? The percentage difference between points x1 and x2,
        where x1 is the current point in time, and x1 is a point t minutes ago
    -> Params Required:
        -> 'period'
'''

class Delta(Indicator):
    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: weather or not we should generate new values for each param belonging
            to this Indicator
        -> value (String) <optional>: dataframe column name to use for calculations
    RETURN:
        -> None
    WHAT: 
        -> calculates and adds the delta for the given value over the given period to the dataset
    '''
    def genData(self, dataset, gen_new_values=True, value='close'):
        period = findParams(self.params, ['period'])[0]
        if gen_new_values:
            period.genValue()
        period_value = int(period.value) 
    
        # calculate percentage difference between x1 and x2 for every point in the dataset
        dataset[self.name] = (dataset[value] - dataset[value].shift(periods=1*period_value))/dataset[value].shift(1*period_value)\
        # points that occur before the period length can just be set to 0
        dataset[self.name][:period_value] = 0
        