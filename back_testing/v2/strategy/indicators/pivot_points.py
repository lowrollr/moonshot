'''
FILE: pivot_points.py
AUTHORS:
    -> Jacob Marshall (marshingjay@gmail.com)
WHAT:
    -> This file contains the Pivot Points Indicator
'''
from v2.strategy.indicators.indicator import Indicator
from v2.utils import findParams
from v2.strategy.indicators.sma import SMA
import pandas

'''
CLASS: PivotPoints
WHAT:
    -> Calculates the pivot point for the given window and adds the approprite column to the dataset
    -> What is slope? --> https://towardsdatascience.com/pivot-points-calculation-in-python-for-day-trading-659c1e92d323
    -> Params Required:
        -> 'period'
'''

class PivotPoints(Indicator):
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
        
        dataset['pp_high' + self.appended_name] = dataset[value].rolling(int(period.value)).max()
        dataset['pp_low' + self.appended_name] = dataset[value].rolling(int(period.value)).min()
        # this is the close price IRL but that skews the data when we compute on a rolling basis
        # will see how this goes
        pp_sma = SMA([period], _name='pp_sma', _appended_name=self.appended_name)
        pp_sma.genData(dataset, gen_new_values=False, value=value)
        dataset['pp_pp' + self.appended_name] = (dataset['pp_high'] + dataset['pp_low'] + dataset['pp_sma']) / 3
        dataset['pp_r1' + self.appended_name] = (2 * dataset['pp_pp']) - dataset['pp_low']
        dataset['pp_s1' + self.appended_name] = (2 * dataset['pp_pp']) - dataset['pp_high']
        dataset['pp_r2' + self.appended_name] = dataset['pp_pp'] + (dataset['pp_high'] - dataset['pp_low'])
        dataset['pp_s2' + self.appended_name] = dataset['pp_pp'] - (dataset['pp_high'] - dataset['pp_low'])
        dataset['pp_r3' + self.appended_name] = dataset['pp_pp'] + (2 * (dataset['pp_high'] - dataset['pp_low']))
        dataset['pp_s3' + self.appended_name] = dataset['pp_pp'] - (2 * (dataset['pp_high'] - dataset['pp_low']))

        # clean up intermediate columns
        del dataset['pp_pp' + self.appended_name]
        del dataset['pp_low' + self.appended_name]
        del dataset['pp_high' + self.appended_name]
        del dataset['pp_sma' + self.appended_name]
