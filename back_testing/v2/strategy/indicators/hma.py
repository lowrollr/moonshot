'''
FILE: hma.py
AUTHORS:
    -> Ross Copeland (rhcopeland101@gmail.com)
WHAT:
    -> This file contains the HMA (Hull Moving Average) Indicator
'''
from v2.utils import findParams
from v2.strategy.indicators.param import Param
from v2.strategy.indicators.indicator import Indicator
from v2.strategy.indicators.wma import WMA
import numpy as np

'''
CLASS: HMA
WHAT:
    -> Implements the HMA Indicator and adds the approprite columns to the dataset
    -> What is HMA? --> https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/hull-moving-average
    -> Params Required:
        -> 'period'
'''
class HMA(Indicator):
    
    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: weather or not we should generate new values for each param belonging
            to this Indicator
        -> value (String) <optional>: dataframe column name to use for calculations
    RETURN:
        -> None
    WHAT: 
        -> computes the hull moving average of the specified value over the given period
        -> Formula: HMA = WMA(2*WMA(n/2) - WMA(n)), sqrt(n)
    TODO:
        -> This has not been tested
    '''
    def genData(self, dataset, gen_new_values=True):

        # param named 'period' must be present
        hma_period = findParams(self.params, ['period'])[0]
        # generate a new period value, if necessary
        if gen_new_values:
            hma_period.genValue()
        
        normal_wma_param = Param(_name='period', _default=hma_period.value)
        normal_wma = WMA([normal_wma_param], _name="normal_wma")
        normal_wma.genData(dataset, gen_new_values=False, value=self.value)

        half_period = int(hma_period.value/2)
        half_period_wma_param = Param(_name="period", _default=half_period)
        half_period_wma = WMA([half_period_wma_param], _name="half_period_wma")
        half_period_wma.genData(dataset, gen_new_values=False, value=self.value)

        dataset["difference"] = (2 * dataset["half_period_wma"]) - dataset["normal_wma"]
        
        final_period = int(np.sqrt(hma_period.value))
        final_period_param = Param(_name="period", _default=final_period)
        final_period_wma = WMA([final_period_param], _name=self.name)
        final_period_wma.genData(dataset, gen_new_values=False, value="difference")
        
        #clean up
        dataset.drop(["difference", "half_period_wma", "normal_wma"], inplace=True, axis=1)

        return [self.name]

    def setDefaultParams(self):
        self.params = [
            Param(5,10000,0,'period',400)
        ]