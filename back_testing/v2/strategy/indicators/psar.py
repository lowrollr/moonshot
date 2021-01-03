'''
FILE: psar.py
AUTHORS:
    -> Ross Copeland (rhcopeland101@gmail.com)
WHAT:
    -> This file contains the PSAR (Parabolic SAR) Indicator
'''

from v2.utils import findParams
from v2.strategy.indicators.indicator import Indicator
from talib import SAR

'''
CLASS: PSAR
WHAT:
    -> Implements the PSAR Indicator and adds the approprite columns to the dataset
    -> What is PSAR? --> https://www.investopedia.com/trading/introduction-to-parabolic-sar/
    -> Params Required:
        -> 'period'
TODO:
    -> replace pyti implementation
'''
class PSAR(Indicator):

    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: weather or not we should generate new values for each param belonging
            to this Indicator
        -> value (String) <optional>: dataframe column name to use for calculations
    RETURN:
        -> None
    WHAT: 
        -> computes the parabolic sar of the specified value over the given period
    '''
    def genData(self, dataset, gen_new_values=True, value='close'):

        # param named 'period' must be present
        period = findParams(self.params, ['period'])[0]
        # generate a new period value, if necessary
        if gen_new_values:
            period.genValue()

        # compute SAR
        dataset[self.name] = SAR(dataset.high, dataset.close, acceleration=0.2, maxiumum=0.2)