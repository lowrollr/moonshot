'''
FILE: smma.py
AUTHORS:
    -> Jacob Marshall (marshingjay@gmail.com)
WHAT:
    -> This file contains the SMMA (Smoothed Moving Average) Indicator
'''

from pyti.smoothed_moving_average import smoothed_moving_average as smma
from v2.strategy.indicators.param import Param
from v2.utils import findParams
from v2.strategy.indicators.indicator import Indicator

'''
CLASS: SMMA
WHAT:
    -> Implements the SMMA Indicator and adds the approprite columns to the dataset
    -> What is SMMA? --> http://www.fxcorporate.com/help/MS/NOTFIFO/i_SMMA.html
    -> Params Required:
        -> 'period'
TODO:
    -> replace pyti implementation
'''
class SMMA(Indicator):

    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: weather or not we should generate new values for each param belonging
            to this Indicator
        -> value (String) <optional>: dataframe column name to use for calculations
    RETURN:
        -> None
    WHAT: 
        -> computes the smoothed moving average of the specified value over the given period
    '''
    def genData(self, dataset, gen_new_values=True):

        # param named 'period' must be present
        period = findParams(self.params, ['period'])[0]
        # generate a new period value, if necessary
        if gen_new_values:
            period.genValue()
        # compute smma
        new_smma = smma(dataset[self.value].tolist(), int(period.value))
        # add to dataset
        dataset[self.name] = new_smma
        return [self.name]

    def setDefaultParams(self):
        self.params = [
            Param(5,10000,0,'period',400)
        ]