'''
FILE: momentum.py
AUTHORS:
    -> Jacob Marshall (marshingjay@gmail.com)
WHAT:
    -> This file contains the Momentum Indicator
'''
from v2.strategy.indicators.indicator import Indicator
from v2.utils import findParams
from talib import MOM
import pandas

'''
CLASS: Momentum
WHAT:
    -> Implements the Momentum Indicator and adds the approprite column to the dataset
    -> What is Momentum? --> https://www.fmlabs.com/reference/default.htm?url=Momentum.htm
    -> Params Required:
        -> 'period'
'''

class Momentum(Indicator):
    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: weather or not we should generate new values for each param belonging
            to this Indicator
        -> value (String) <optional>: dataframe column name to use for calculations
    RETURN:
        -> None
    WHAT: 
        -> calculates and adds the Momentum of the specified value over the given period to the dataset
    '''
    def genData(self, dataset, gen_new_values=True, value='close'):
        period = findParams(self.params, ['period'])[0]
        
        if gen_new_values:
            
            period.genValue()
        
        dataset[self.name] = MOM(dataset[value], period.value)
        
        