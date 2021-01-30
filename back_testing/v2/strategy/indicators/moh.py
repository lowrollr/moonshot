'''
FILE: moh.py
AUTHORS:
    -> Ross Copeland (rhcopeland101@gmail.com)
WHAT:
    -> This file contains the MOH (Minute Of Hour) Indicator
'''

import pandas
from datetime import datetime

from v2.strategy.indicators.param import Param
from v2.utils import findParams
from v2.strategy.indicators.indicator import Indicator

'''
CLASS: MOH
WHAT:
    -> Implements the MOH Indicator and adds the approprite columns to the dataset
    -> What is MOH? --> It's the day of the week silly
    -> Params Required:
        -> N/A
'''
class MOH(Indicator):
    
    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: weather or not we should generate new values for each param belonging
            to this Indicator
        -> value (String) <optional>: dataframe column name to use for calculations
    RETURN:
        -> None
    WHAT: 
        -> computes the minute of the hour from the timestamp of the specified value over the given period
    '''
    def genData(self, dataset, gen_new_values=True):
        dataset[self.name] = dataset['time'].apply(lambda x: datetime.fromtimestamp(x//1000).minute)

        return [self.name]

    def setDefaultParams(self):
        self.params = [
        ]