'''
FILE: notebook_utils.py
AUTHORS:
    -> Jacob Marshall (marshingjay@gmail.com) 
WHAT:
    -> This file contains utility functions associated with the fetching 
        and manipulation of indicators for research notebooks
    -> Backtesting code should avoid calling these if possible
'''
from pyclbr import readmodule
from importlib import import_module
from inspect import isclass, getmembers
from v2.strategy.indicators.param import Param
from v2.strategy.indicators.indicator import Indicator
from v2.utils import findParams
from load_config import load_config
from v2.model import Trading
from alive_progress import alive_bar
from sklearn.preprocessing import MinMaxScaler, QuantileTransformer
'''
ARGS:
    -> indicator_list ([String]): list of strings that are matched to Indicator objects
    -> param_specification ({String: Value}) <optional>: maps indicator params to values 
RETURN:
    -> None
WHAT: 
    -> initializes each indicator specified in indicator_list (must match strings correctly)
    -> allows for params to be specified in param_specification (again, must match strings correctly)
    -> if a param is not specified in param_specification, a hard-coded default value is used
    -> This is a quality-of-life function for notebooks, should not be used anywhere else
    -> DO NOT CALL THIS FUNCTION UNLESS YOU ARE DOING SO FROM A NOTEBOOK >:(
'''
def fetchIndicators(indicator_list, param_specification={}):
    indicator_objects = []
    for indicator in indicator_list:
        base_dir = 'v2.strategy.indicators.'
        module = import_module(base_dir + indicator.lower())
        indicator_object = None
        local_class = list(readmodule(module.__name__).values())[0].module
        for mod in dir(module):
            obj = getattr(module, mod)
            if isclass(obj) and obj.__module__ == local_class:
                indicator_object = obj
                break
        if indicator_object:
            ind_obj = indicator_object(_params=[])
            ind_obj.setDefaultParams()
            if indicator in param_specification:
                params_to_set = findParams(ind_obj.params, param_specification[indicator].keys())
                for p in params_to_set:
                    p.value = param_specification[indicator][p.name]
            indicator_objects.append(ind_obj)
        else:
            raise Exception(f'Indicator object <{indicator}> could not be found!')
    
    return indicator_objects


'''
ARGS:
    -> dataset (DataFrame): dataset to add indicators to
    -> indicators ([Indicator]): list of indicator objects that need added to the dataset
RETURN:
    -> None
WHAT: 
    -> Generates data for each Indicator and puts it in the dataset
'''
def genDataForAll(dataset, indicators):
    names = []
    for x in indicators:
        names.append(x.genData(dataset, gen_new_values=False))
    return names


def generateSpans(dataset, indicator_name, column_name, param_name, param_values, gen_data=True):
    names = []
    for x in param_values:
        ind = fetchIndicators([indicator_name], param_specification={indicator_name:{param_name: x}})[0]
        name = f'{type(ind).__name__}_{column_name}_{param_name}_{x}'
        ind.name = name
        names.append(name)
        if gen_data:
            ind.genData(dataset, gen_new_values=False, value=column_name)

    return names


def load_data(indicators, param_spec={}, spans={}, scale=''):
    features = []
    model = Trading(load_config('config.hjson'))
    dataset_list = []
    for g,n in model.df_groups:
        print(f'Loading data from {n}...')
        
        for i,d in enumerate(g):
            print(f'Loading data from chunk {i}...')
            with alive_bar(length=len(d), spinner='vertical') as bar:
                features.extend(genDataForAll(fetchIndicators(indicators, param_spec)))