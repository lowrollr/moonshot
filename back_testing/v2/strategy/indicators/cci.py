'''
FILE: cci.py
AUTHORS:
    -> Ross Copeland (rhcopeland101@gmail.com)
WHAT:
    -> This file contains the CCI (Commodity Channel Index) Indicator
'''
from v2.utils import findParams
from v2.strategy.indicators.param import Param
from v2.strategy.indicators.indicator import Indicator
from v2.strategy.indicators.sma import SMA
import numpy as np
from talib import CCI as talib_CCI

'''
CLASS: CCI
WHAT:
    -> Implements the CCI Indicator and adds the approprite columns to the dataset
    -> What is CCI? --> https://www.investopedia.com/terms/c/commoditychannelindex.asp
    -> Params Required:
        -> 'period'
'''
class CCI(Indicator):
    
    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: weather or not we should generate new values for each param belonging
            to this Indicator
        -> value (String) <optional>: dataframe column name to use for calculations
    RETURN:
        -> None
    WHAT: 
        -> computes the commodity channel index of the specified value over the given period
        -> Formula: CCI = (TP - SMA(TP)) / (0.015 * Mean Deviation)
            TP = High+Low+Close) ÷ 3
    TODO:
        -> This has not been tested
    '''
    def genData(self, dataset, gen_new_values=True, value='close'):

        # param named 'period' must be present
        period = findParams(self.params, ['period'])[0]
        # generate a new period value, if necessary
        if gen_new_values:
            period.genValue()
        
        # dataset["cci_high"] = dataset[value].rolling(window=int(period.value)).max()
        # dataset["cci_low"] = dataset[value].rolling(window=int(period.value)).min()
        # dataset["cci_tp"] = (dataset["cci_high"] + dataset["cci_low"] + dataset[value]) / 3

        # cci_mean_dev = np.mean(np.absolute(dataset["cci_tp"] - np.mean(dataset["cci_tp"])))

        # sma_tp = SMA([period], _name="cci_sma_tp")
        # sma_tp.genData(dataset, gen_new_values=False, value="cci_tp")

        # dataset[self.name] = (dataset["cci_tp"] - dataset["cci_sma_tp"]) / (0.015 * cci_mean_dev)

        # #clean up
        # dataset.drop(["cci_high", "cci_low", "cci_tp", "cci_sma_tp"], inplace=True, axis=1)
        dataset[self.name] = talib_CCI(dataset.high, dataset.low, dataset.close, timeperiod=period.value)

    def setDefaultParams(self):
        self.params = [
            Param(5,10000,0,'period',400)
        ]