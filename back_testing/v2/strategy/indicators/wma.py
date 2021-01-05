'''
FILE: wma.py
AUTHORS:
    -> Ross Copeland (rhcopeland101@gmail.com)
WHAT:
    -> This file contains the WMA (Weighted Moving Average) Indicator
'''
from v2.utils import findParams
from v2.strategy.indicators.indicator import Indicator
from v2.strategy.indicators.param import Param
import numpy as np
from talib import WMA as talib_WMA

'''
CLASS: WMA
WHAT:
    -> Implements the WMA Indicator and adds the approprite columns to the dataset
    -> What is WMA? --> https://corporatefinanceinstitute.com/resources/knowledge/trading-investing/weighted-moving-average-wma/
    -> Params Required:
        -> 'period'
'''
class WMA(Indicator):
    
    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: weather or not we should generate new values for each param belonging
            to this Indicator
        -> value (String) <optional>: dataframe column name to use for calculations
    RETURN:
        -> None
    WHAT: 
        -> computes the weighted moving average of the specified value over the given period
    TODO:
        -> This has not been tested
    '''
    def genData(self, dataset, gen_new_values=True, value='close'):

        # param named 'period' must be present
        period = findParams(self.params, ['period'])[0]
        # generate a new period value, if necessary
        if gen_new_values:
            period.genValue()
        
        # weights = np.arange(1, period.value + 1)
        # # compute simple moving average and add to the dataset
        # dataset[self.name] = dataset[value].rolling(window=int(period.value)).apply(lambda prices: np.dot(prices, weights)/weights.sum(), raw=True)

        dataset[self.name] = talib_WMA(dataset[value], timeperiod=period.value)

    def setDefaultParams(self):
        self.params = [
            Param(5,10000,0,'period',400)
        ]