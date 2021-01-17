'''
FILE: bop.py
AUTHORS:
    -> Ross Copeland (marshingjay@gmail.com)
WHAT:
    -> This file contains the BOP (Balance of Power) Indicator
'''

import pandas

from v2.strategy.indicators.param import Param
from v2.utils import findParams
from v2.strategy.indicators.indicator import Indicator
from talib import BOP as talib_BOP

'''
CLASS: BOP
WHAT:
    -> Implements the BOP Indicator and adds the approprite columns to the dataset
    -> What is BOP? --> https://www.theforexgeek.com/balance-of-power/
    -> Params Required:
        -> 'period'
'''
class BOP(Indicator):
    
    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: weather or not we should generate new values for each param belonging
            to this Indicator
        -> value (String) <optional>: dataframe column name to use for calculations
    RETURN:
        -> None
    WHAT: 
        -> computes the balance of power of the specified value over the given period
    '''
    def genData(self, dataset, gen_new_values=True):
        # generate a new period value, if necessary
        if gen_new_values:
            pass
        
        dataset[self.name] = talib_BOP(dataset.open, dataset.high, dataset.low, dataset.close)

        return [self.name]

    def setDefaultParams(self):
        self.params = [
            Param(5,10000,0,'period',50)
        ]