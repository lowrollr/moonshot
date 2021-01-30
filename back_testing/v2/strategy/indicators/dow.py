'''
FILE: dow.py
AUTHORS:
    -> Ross Copeland (rhcopeland101@gmail.com)
WHAT:
    -> This file contains the DOW (Day Of Week) Indicator
'''

import pandas
from datetime import datetime

from v2.strategy.indicators.param import Param
from v2.utils import findParams
from v2.strategy.indicators.indicator import Indicator

'''
CLASS: DOW
WHAT:
    -> Implements the DOW Indicator and adds the approprite columns to the dataset
    -> What is DOW? --> It's the day of the week silly
    -> Params Required:
        -> N/A
'''
class DOW(Indicator):
    
    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: weather or not we should generate new values for each param belonging
            to this Indicator
        -> value (String) <optional>: dataframe column name to use for calculations
    RETURN:
        -> None
    WHAT: 
        -> computes the day of the week from the timestamp of the specified value over the given period
    '''
    def genData(self, dataset, gen_new_values=True):
        dataset[self.name] = dataset['time'].apply(lambda x: datetime.fromtimestamp(x//1000).weekday())

        return [self.name]

    def setDefaultParams(self):
        self.params = [
        ]