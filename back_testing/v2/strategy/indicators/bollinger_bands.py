'''
FILE: bollinger_bands.py
AUTHORS:
    -> Jacob Marshall (marshingjay@gmail.com)
WHAT:
    -> This file contains the Bollinger Band Indicator
'''
from v2.strategy.indicators.indicator import Indicator
from v2.utils import findParams
from v2.strategy.indicators.sma import SMA
import pandas

'''
CLASS: EMA
WHAT:
    -> Implements the Bollinger Bands Indicator and adds the approprite columns to the dataset
    -> What are Bollinger Bands? --> 
    -> Params Required:
        -> 'period'
'''

class BollingerBands(Indicator):
    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: weather or not we should generate new values for each param belonging
            to this Indicator
        -> value (String) <optional>: dataframe column name to use for calculations
    RETURN:
        -> None
    WHAT: 
        -> calculates and adds the Bollinger Bands of the specified value over the given period to the dataset
    '''
    def genData(self, dataset, gen_new_values=True, value='close'):
        period = findParams(self.params, ['period'])[0]
        
        boll_sma = SMA([period], _name='boll_sma', _appended_name=self.appended_name)
        boll_sma.genData(dataset, gen_new_values=gen_new_values, value=value)
        dataset['boll_stdev'] = dataset[value].rolling(int(period.value)).std()
        dataset['boll_upper' + self.appended_name] = dataset['boll_sma'] + (dataset['boll_stdev'] * 2)
        dataset['boll_lower' + self.appended_name] = dataset['boll_sma'] - (dataset['boll_stdev'] * 2)

        # clean up intermediate columns
        del dataset['boll_stdev']
        del dataset['boll_sma' + self.appended_name]

        