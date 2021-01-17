'''
FILE: pattern.py
AUTHORS:
    -> Ross Copeland (rhcopeland101@gmail.com)
WHAT:
    -> This file contains the wrapper for using all pattern Indicators
'''
from v2.utils import findParams
from v2.strategy.indicators.param import Param
from v2.strategy.indicators.indicator import Indicator
import importlib
import os
import inspect

'''
CLASS: Pattern
WHAT:
    -> Implements all the pattern Indicator and adds the approprite columns to the dataset
    -> What are pattern indicators? --> https://www.investopedia.com/articles/active-trading/092315/5-most-powerful-candlestick-patterns.asp
    -> Params Required:
        -> 'period'
'''
class Pattern(Indicator):
        
    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: weather or not we should generate new values for each param belonging
            to this Indicator
        -> value (String) <optional>: dataframe column name to use for calculations
    RETURN:
        -> None
    WHAT: 
        -> computes all pattern indicators of the specified value over the given period
    TODO:
        -> This has not been tested
    '''
    def genData(self, dataset, gen_new_values=True):
        period = findParams(self.params, ['period'])[0]

        #dynamically fetch all indicators in paterns dir
        base_module = 'v2.strategy.indicators.patterns.'
        pattern_indicators = []
        pattern_files = os.listdir('v2/strategy/indicators/patterns')
        for f in pattern_files:
            mod_name = f.split(".py")[0]
            mod_path = base_module + mod_name
            module = importlib.import_module(mod_path)
            for mod in dir(module):
                obj = getattr(module, mod)
                if inspect.isclass(obj) and issubclass(obj, Indicator) and obj != Indicator:
                    pattern_indicators.append(obj)

        indicator_names = []

        for pattern in pattern_indicators:
            pattern_ind = pattern(_params=[])
            indicator_names.append(pattern_ind.genData(dataset=dataset))

        if period.value != 0:
            for col in indicator_names:
                dataset[col] = dataset[col].rolling(period.value).apply(self.pattern_rolling)

        return indicator_names

    def setDefaultParams(self):
        self.params = [
            Param(0,50,0,'period',0)
        ]

    def pattern_rolling(self, val_arr):
        min_roll = min(val_arr)
        max_roll = max(val_arr)
        if (min_roll == 0 and max_roll == 0) or (min_roll != 0 and max_roll != 0) :
            return 0
        if max_roll != 0:
            return 1
        return -1
        