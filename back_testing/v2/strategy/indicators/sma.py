'''
FILE: sma.py
AUTHORS:
    -> Jacob Marshall (marshingjay@gmail.com)
WHAT:
    -> This file contains the SMA (Simple Moving Average) Indicator
'''
from v2.strategy.indicators.param import Param
from v2.strategy.indicators.indicator import Indicator
from v2.utils import findParams

from talib import SMA as talib_SMA

'''
CLASS: SMA
WHAT:
    -> Implements the SMA Indicator and adds the approprite columns to the dataset
    -> What is SMA? --> https://www.investopedia.com/terms/s/sma.asp
    -> Params Required:
        -> 'period'
'''
class SMA(Indicator):
    
    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: weather or not we should generate new values for each param belonging
            to this Indicator
        -> value (String) <optional>: dataframe column name to use for calculations
    RETURN:
        -> None
    WHAT: 
        -> computes the simple moving average of the specified value over the given period
    '''
    def genData(self, dataset, gen_new_values=True, value='close'):

        # param named 'period' must be present
        period = findParams(self.params, ['period'])[0]
        # generate a new period value, if necessary
        if gen_new_values:
            period.genValue()
        
        # compute simple moving average and add to the dataset
        dataset[self.name] = talib_SMA(dataset[value], timeperiod=period.value)
        # dataset[self.name] = dataset[value].rolling(int(period.value)).mean()
    
    def setDefaultParams(self):
        self.params = [
            Param(5,10000,0,'period',400)
        ]