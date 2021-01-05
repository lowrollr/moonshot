'''
FILE: variance.py
AUTHORS:
    -> Jacob Marshall (marshingjay@gmail.com)
    -> Ross Copeland (rhcopeland101@gmail.com)
WHAT:
    -> This file contains the Variance Indicator
'''

import pandas
import numpy as np

from v2.strategy.indicators.indicator import Indicator
from v2.strategy.indicators.param import Param
from v2.utils import findParams

'''
CLASS: Variance
WHAT:
    -> Calculates variance and adds the approprite column to the dataset
    -> What is variance? --> https://en.wikipedia.org/wiki/Variance
    -> Params Required:
        -> 'period'
'''
class Variance(Indicator):
    '''
    ARGS:
        -> var_std (Float): standard deviation of the window
        -> var_mean (Float) <optional>: the mean of the window
        -> cur_val (Float) <optional>: current value to process the varaince for
    RETURN:
        -> None
    WHAT: 
        -> computes the variance of the specified value over the given period
    '''
    def process_variance(self, var_std, var_mean, cur_var):
        if cur_var > var_mean + (2 * var_std):
            return 0.5
        elif cur_var < max(0, var_mean - (2 * var_std)):
            return 0.1
        else:
            span = (var_mean + (2 * var_std)) - (var_mean - (2 * var_std))
            unscaled_coeff = float(cur_var - (var_mean - (2 * var_std))) / float(span)

            return 0.1 + (unscaled_coeff * 0.4)

    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: weather or not we should generate new values for each param belonging
            to this Indicator
        -> value (String) <optional>: dataframe column name to use for calculations
    RETURN:
        -> None
    WHAT: 
        -> adds the variance of the specified value over the given period
    '''
    def genData(self, dataset, gen_new_values=True, value='close'):
        period = findParams(self.params, ['period'])[0]
        if gen_new_values:
            period.genValue()

        dataset[self.name] = dataset[value].rolling(window=int(period.value)).var()

        stop_loss_percentage = findParams(self.params, ['stop_loss_percentage'])[0]
        if stop_loss_percentage:
            var_std = np.std(dataset['variance'])
            avg_var = np.mean(dataset['variance'])
            dataset['stop_loss_percentage'] = dataset.apply(lambda x: self.process_variance(var_std, avg_var, x.variance), axis=1)

    def setDefaultParams(self):
        self.params = [
            Param(5,10000,0,'period',400)
        ]
