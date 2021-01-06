'''
FILE: notebook_utils.py
AUTHORS:
    -> Jacob Marshall (marshingjay@gmail.com) 
WHAT:
    -> This file contains utility functions associated with the fetching 
        and manipulation of indicators for research notebooks
    -> Backtesting code should avoid calling these if possible
'''
from pandas import concat
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
        new_names = x.genData(dataset, gen_new_values=False)
        names.extend(new_names)
    return names


'''
ARGS:
    -> dataset (DataFrame): dataset to add indicator spans to
    -> indicator_name (String): indicator applied to column, name corresponds to filename for dynamic importing
    -> column_name (String): column already in the dataframe to apply the indicator to
    -> param_name (String): parameter of the indicator to vary
    -> param_values (String): values for the given param, a dataframe column will be generated for each

RETURN:
    -> names (String): list of column names generated
WHAT: 
    -> Generates data for each the given indicator applied to a column for each given param value
'''
def generateSpans(dataset, indicator_name, column_name, param_name, param_values, gen_data=True):
    names = []
    for x in param_values:
        # grab new instantiated indicator objects corresponding to each name passed, set the param accordingly
        ind = fetchIndicators([indicator_name], param_specification={indicator_name:{param_name: x}})[0]
        # construct the column name
        name = f'{type(ind).__name__}_{column_name}_{param_name}_{x}'
        ind.name = name
        names.append(name)
        # generate the data and add it to the dataset
        if gen_data:
            ind.genData(dataset, gen_new_values=False, value=column_name)

    return names

'''
ARGS:
    -> optimal (Float): optimal score from an optimal buy/sell points algorithm implementation
    -> threshold (Float): Value between 0 and 1 to accept optimal scores for
    -> mode (String): 'buy' or 'sell' corresponding to whether to consider buy or sell values
RETURN:
    -> (Float): 1.0 if the point should be specified as buy/sell point, 0.0 if not
WHAT: 
    -> Determines whether or not a given point should be considered an optimal buy/sell point
        by filtering out scores over a certain threshold
'''
def filter_optimal(optimal, threshold, mode):
    if mode == 'both:':
        if optimal > threshold:
            return 1.0
        elif optimal < -1*threshold:
            return -1.0
        else:
            return 0.0
    elif mode == 'buy':
        if optimal > threshold:
            return 1.0
        else:
            return 0.0
    else:
        if optimal < -1*(threshold):
            return 1.0
        else:
            return 0.0

'''
ARGS:
    -> indicators ([String]): list of indicators to add to the dataset
    -> param_spec ({String:{String:Value}}): dictionary defining parameter values to set,
        maps indicator names to Param:Value pairs
    -> optimal_threshold (Float): threshold for considering optimal scores, if using an optimal indicator
    -> optimal_mode (String): should be either 'buy' or 'sell' (whether we are considering buy or sell points)
    -> spans ([{String: Value}]): list of dictionarires defining arguments to be passed to the generateSpans function
    -> scale (String): specifies which scaler to use
RETURN:
    -> dataset (Dataframe): dataset with all specified features added to it, linking together chunks from each currency 
    -> names ([String]): list of strings corresponding to non-optimal features added
WHAT: 
    -> wrapper for the common operations necessary to configure a dataset in a notebook
    -> returns the generated dataset and a list of the features added
    -> will add optimal features if specified but those will NOT be included in the returned features list
'''
def loadData(indicators, param_spec={}, optimal_threshold=0.9, optimal_mode='buy', spans={}, scale=''):
    features = []
    model = Trading(load_config('config.hjson'))
    dataset_list = []
    compiling_features = True
    for g,n in model.df_groups:
        coin_dataset = []
        print(f'Loading data from {n}...')
        for i,d in enumerate(g):
            print(f'Loading data from chunk {i}...')
            new_features = genDataForAll(dataset=d, indicators=fetchIndicators(indicators, param_spec))
            if 'Optimal_v2' in new_features:
                new_features.remove('Optimal_v2')
                d['Optimal_v2'] = d.apply(lambda x: filter_optimal(x.Optimal_v2, optimal_threshold, optimal_mode),  axis=1)
            if 'Optimal' in new_features:
                new_features.remove('Optimal')
                d['Optimal'] = d.apply(lambda x: filter_optimal(x.filter_Optimal, optimal_threshold, optimal_mode),  axis=1)
            if compiling_features:
                features.extend(new_features)
            for span in spans:
                new_features = generateSpans(dataset=d, 
                                            indicator_name=span['indicator_name'],
                                            column_name=span['column_name'],
                                            param_name=span['param_name'],
                                            param_values=span['param_values'])
                if compiling_features:
                    features.extend(new_features)
            coin_dataset.append(d)
            compiling_features = False

        coin_dataset = concat(coin_dataset)
        if scale:
            scaler = None
            if scale == 'minmax':
                scaler = MinMaxScaler()

            elif scale == 'quartile':
                scaler = QuantileTransformer(n_quantiles=100)
            else:
                raise Exception(f'Unknown scaler: {scaler}')

            coin_dataset[features] = scaler.fit_transform(coin_dataset[features])  
        dataset_list.append(coin_dataset)
        
    dataset = concat(dataset_list)
    dataset.reset_index(inplace=True, drop=True)
        

    return dataset, features