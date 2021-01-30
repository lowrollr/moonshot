'''
FILE: tod.py
AUTHORS:
    -> Ross Copeland (rhcopeland101@gmail.com)
WHAT:
    -> This file contains the TOD (Time Of Day) Indicator
'''

import pandas
from datetime import datetime

from v2.strategy.indicators.param import Param
from v2.utils import findParams
from v2.strategy.indicators.indicator import Indicator

'''
CLASS: TOD
WHAT:
    -> Implements the TOD Indicator and adds the approprite columns to the dataset
    -> What is TOD? --> It's the hour of the day silly
    -> Params Required:
        -> N/A
'''
class TOD(Indicator):
    
    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: weather or not we should generate new values for each param belonging
            to this Indicator
        -> value (String) <optional>: dataframe column name to use for calculations
    RETURN:
        -> None
    WHAT: 
        -> computes the time of day from the timestamp of the specified value over the given period
    '''
    def genData(self, dataset, gen_new_values=True):
        dataset[self.name] = dataset['time'].apply(lambda x: datetime.fromtimestamp(x//1000).hour)

        return [self.name]

    def setDefaultParams(self):
        self.params = [
        ]