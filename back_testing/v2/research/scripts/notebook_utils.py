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
import numpy as np
from sklearn.model_selection import train_test_split
import pandas as pd
from sklearn.utils import class_weight
import matplotlib.pyplot as plt
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
    if mode == 'both':
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
    elif mode == "sell":
        if optimal < -1*(threshold):
            return 1.0
        else:
            return 0.0
    else:
        raise ValueError("Did not provide either buy sell or both to the optimal_threshold dict")

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
def loadData(indicators, param_spec={}, optimal_threshold={"buy":0.9}, spans={}, scale=''):
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
            if 'Optimal_v2' in new_features or 'Optimal' in new_features:
                optimal_col_name = 'Optimal_v2' if 'Optimal_v2' in new_features else 'Optimal'
                if len(list(optimal_threshold.keys())) == 1:
                    threshold_key = list(optimal_threshold.keys())[0]

                    d["optimal"] = d.apply(lambda x: filter_optimal(x.Optimal_v2, optimal_threshold[threshold_key], threshold_key),  axis=1)

                    d.drop(optimal_col_name, inplace=True, axis=1)
                elif len(optimal_threshold.keys()) == 2:
                    for key in list(optimal_threshold.keys()):
                        d["optimal_" + key] = d.apply(lambda x: filter_optimal(x.Optimal_v2, optimal_threshold[key], key),  axis=1)
                    d.drop(optimal_col_name, axis=1, inplace=True)

                else: raise Exception("Please provide either one or two thresholds")
                
                new_features.remove(optimal_col_name)

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

            #drop columns that have nan
            # if d.columns.to_series()[np.isnan(d).all()] is not None:
            #     for val in d.columns.to_series()[np.isinf(d).any()]:
            #         if val in features:
            #             features.remove(val)

            # d.dropna(inplace=True)
            # d.replace([-np.inf], np.inf, inplace=True)

            if d.columns.to_series()[np.isinf(d).any()] is not None:
                for val in d.columns.to_series()[np.isinf(d).any()]:
                    if val in features:
                        features.remove(val)

                    d[val].replace([np.inf], np.nan, inplace=True)
                    d[val].replace([np.nan], d[val].max(), inplace=True)

            d[features] = scaler.fit_transform(d[features])

            coin_dataset[features] = scaler.fit_transform(coin_dataset[features])  
        dataset_list.append(coin_dataset)
        
    dataset = concat(dataset_list)
    dataset.reset_index(inplace=True, drop=True)
        

    return dataset, features

def splitData(dataset, split_size=0.2, y_column_name="Optimal_v2", shuffle_data=False, balance_unbalanced_data=False, balance_info=None):
    if not balance_unbalanced_data:
        return train_test_split(dataset.drop([y_column_name], axis=1), dataset[[y_column_name]], test_size=split_size, shuffle=shuffle_data)

    if balance_info != None:
        train, test = train_test_split(dataset, test_size=split_size, shuffle=shuffle_data)
        min_class_signals = train[train[y_column_name] != balance_info['superset_class_val']]
        not_signals = train[train[y_column_name] == balance_info['superset_class_val']]

        sampled_not_signals = not_signals.sample(n=min(len(min_class_signals) * balance_info["multiplier_val"], len(not_signals)), random_state=69420, axis=0)

        balanced_data_all = pd.concat([sampled_not_signals, min_class_signals])

        if balance_info['randomize_concat']:
            balanced_data_all = balanced_data_all.sample(frac=1).reset_index(drop=True)

        return balanced_data_all.drop([y_column_name], axis=1), test.drop([y_column_name], axis=1), balanced_data_all[[y_column_name]], test[[y_column_name]]


    raise Exception("when balance == true balance_info must specify params for balancing. Specify in the form of:\
        {'multiplier_val':4, 'superset_class_val':0, 'randomize_concat':true}")

def getWeights(y_dataset):
    weights = class_weight.compute_class_weight('balanced', np.unique(y_dataset.to_numpy()[:,0]), y_dataset.to_numpy()[:,0])
    return {i : weights[i] for i in range(len(np.unique(y_dataset.values)))}

def insert_buys(row):
    if row.predict_buy > 0.6:
        return row.close
    # if row.predict == 2.0 :# and heat_val > 0.6:
    #     return row.close
    else:
        return None

def insert_sells(row):
    if row.predict_sell > 0.5:
        return row.close
    # if row.predict == 0.0:
    #     return row.close
    else:
        return None

def classifyPoints(clf, dataset, predict_proba=False, proba_thresh=0.7, plot_optimal=False, optimal=None):
    if not predict_proba:
        dataset["classify"] = clf.predict(dataset.drop("close", axis=1).values)
    else:
        dataset["predict"] = clf.predict_proba(dataset.drop("close", axis=1).values)[:,1]
        dataset["classify"] = dataset["predict"].apply(lambda x: filter_optimal(x, proba_thresh, "buy"))
        dataset.drop("predict", axis=1, inplace=True)

    if plot_optimal:
        return pd.concat([dataset[["close", "classify"]], optimal])

    return dataset[["close", "classify"]]


def inputPrice(row):
    if row.classify:
        return row.close
    return np.nan

def graphPoints(df, mode="buy", plot_optimal=False):
    color = "red" if mode == "buy" else "green"

    df["classify"] = df["classify"].apply(lambda x: inputPrice(x))

    plt.scatter(df.index, df['classify'], color=color)

    if plot_optimal:
        df['optimal_' + mode] = df['optimal_' + mode].apply(lambda x: inputPrice(x))

        plt.scatter(df.index, df['optimal_' + mode], color="purple")

    plt.plot(df.index, df['close'], color='blue')