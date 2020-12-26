'''
FILE: tema.py
AUTHORS:
    -> Ross Copeland (rhcopeland101@gmail.com)
WHAT:
    -> This file contains the TEMA (Triple Exponential Moving Average) Indicator
'''
from v2.utils import findParams
from v2.strategy.indicators.param import Param
from v2.strategy.indicators.indicator import Indicator
from v2.strategy.indicators.ema import EMA
import numpy as np

'''
CLASS: TEMA
WHAT:
    -> Implements the TEMA Indicator and adds the approprite columns to the dataset
    -> What is TEMA? --> https://www.investopedia.com/terms/t/triple-exponential-moving-average.asp
    -> Params Required:
        -> 'period'
'''
class TEMA(Indicator):
    
    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: weather or not we should generate new values for each param belonging
            to this Indicator
        -> value (String) <optional>: dataframe column name to use for calculations
    RETURN:
        -> None
    WHAT: 
        -> computes the triple exponential moving average of the specified value over the given period
        -> Formula: TEMA = (3*EMA - 3*EMA(EMA)) + EMA(EMA(EMA))
    TODO:
        -> This has not been tested
    '''
    def genData(self, dataset, gen_new_values=True, value='close'):

        # param named 'period' must be present
        tema_period = findParams(self.params, ['period'])[0]
        # generate a new period value, if necessary
        if gen_new_values:
            tema_period.genValue()
        
        ema_param = Param(_name="period", _default=tema_period.value)
        normal_ema = EMA([ema_param], _name="normal_ema")
        normal_ema.genData(dataset, gen_new_values=False, value=value)

        double_ema = EMA([ema_param], _name="double_ema")
        double_ema.genData(dataset, gen_new_values=False, value="normal_ema")

        triple_ema = EMA([ema_param], _name="temp_triple_ema")
        triple_ema.genData(dataset, gen_new_values=False, value="double_ema")

        dataset[self.name] = ((3 * dataset["normal_ema"]) - ( 3 * dataset["double_ema"])) + dataset["temp_triple_ema"]

        

        #clean up
        dataset.drop(["normal_ema", "double_ema", "temp_triple_ema"], inplace=True, axis=1)