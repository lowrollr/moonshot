'''
FILE: slope.py
AUTHORS:
    -> Jacob Marshall (marshingjay@gmail.com)
WHAT:
    -> This file contains the Slope Indicator
'''
from v2.strategy.indicators.indicator import Indicator
from v2.utils import findParams
import pandas

'''
CLASS: Slope
WHAT:
    -> Calculates the slope for the given window and adds the approprite column to the dataset
    -> What is slope? --> https://en.wikipedia.org/wiki/Slope
    -> Params Required:
        -> 'period'
'''

class Slope(Indicator):
    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: weather or not we should generate new values for each param belonging
            to this Indicator
        -> value (String) <optional>: dataframe column name to use for calculations
    RETURN:
        -> None
    WHAT: 
        -> calculates and adds the slope of the specified value over the given period to the dataset
    '''
    def genData(self, dataset, gen_new_values=True, value='close'):
        period = findParams(self.params, ['period'])[0]
        if gen_new_values:
            period.genValue()

        dataset['slope'] = (dataset[value].rolling(window=int(period.value)).max() - dataset[value].rolling(window=int(period.value)).min()) / dataset[value].rolling(window=int(period.value)).max()