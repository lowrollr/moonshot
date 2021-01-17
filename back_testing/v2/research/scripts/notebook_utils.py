'''
FILE: notebook_utils.py
AUTHORS:
    -> Jacob Marshall (marshingjay@gmail.com) 
    -> Ross Copeland (rhcopeland101@gmail.com)
WHAT:
    -> This file contains utility functions associated with the fetching 
        and manipulation of indicators for research notebooks
    -> Backtesting code should avoid calling these if possible
'''
from pandas import concat, read_csv
from pyclbr import readmodule
from importlib import import_module
from inspect import isclass, getmembers
from v2.strategy.indicators.param import Param
from v2.strategy.indicators.indicator import Indicator
from v2.strategy.indicators.optimal import Optimal
from v2.strategy.indicators.optimal_v2 import Optimal_v2
import pickle
from v2.utils import findParams, realtimeScale
from load_config import load_config
from v2.model import Trading
from alive_progress import alive_bar
from sklearn.preprocessing import MinMaxScaler, QuantileTransformer
import tensorflow as tf
from tensorflow import keras
import os
import numpy as np
from sklearn.model_selection import train_test_split
import pandas as pd
from sklearn.utils.class_weight import compute_class_weight
import matplotlib.pyplot as plt
from concurrent.futures import ThreadPoolExecutor
import copy
from itertools import repeat
from glob import glob
import multiprocessing as mp

"""
"""
class notebookUtils:
    def __init__(self):
        pass

    '''
    ARGS:
        -> indicator_list ([String, String]): list of strings that are matched to Indicator objects paired with strings matched to the column
            that the indicator will be applied to
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
    def fetchIndicators(self, indicator_list, param_specification={}):
        indicator_objects = []
        for indicator, value in indicator_list:
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
                ind_obj = indicator_object(_params=[], _value=value)
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
    def genDataForAll(self, dataset, indicators):
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
    def generateSpans(self, dataset, indicator_name, column_name, param_name, param_values, gen_data=True):
        names = []
        inds = []
        for x in param_values:
            # grab new instantiated indicator objects corresponding to each name passed, set the param accordingly
            ind = self.fetchIndicators([[indicator_name, column_name]], param_specification={indicator_name:{param_name: x}})[0]
            # construct the column name
            name = f'{type(ind).__name__}_{column_name}_{param_name}_{x}'
            ind.name = name
            names.append(name)
            # generate the data and add it to the dataset
            inds.append(ind)
            if gen_data:
                ind.genData(dataset, gen_new_values=False)

        return names, inds

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
    def filter_optimal(self, optimal, threshold, mode):
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
    def loadData(self, indicators, param_spec={}, optimal_threshold={"buy":0.9}, spans={}, test=False, test_coin='BTC', test_freq=1, scale='', minmaxwindowsize=15000):
        features = []
        indicator_objs = []
        groups = None
        if not test:
            model = Trading(load_config('config.hjson'))
            groups = model.df_groups
        else:
            dataset_file = f'historical_data/binance/{test_coin}/{test_freq}m/{test_coin}USDT-{test_freq}m-data_chunk000001.csv'
            dataset = read_csv(dataset_file)
            dataset = dataset[['close_time', 'high', 'low', 'close', 'open', 'volume']]
            dataset.rename(columns={'close_time': 'time'}, inplace=True)
            groups = [[[dataset], f'{test_coin}USDT-{test_freq}m']]

        dataset_list = []
        compiling_features = True
        for g,n in groups:
            coin_dataset = []
            print(f'Loading data from {n}...')
            for i,d in enumerate(g):
                print(f'Loading data from chunk {i}...')
                new_indicators = self.fetchIndicators(indicators, param_spec)
                
                new_features = self.genDataForAll(dataset=d, indicators=new_indicators)
                new_indicators = [x for x in new_indicators if type(x) not in [Optimal, Optimal_v2]]
                if 'Optimal_v2' in new_features or 'Optimal' in new_features:
                    optimal_col_name = 'Optimal_v2' if 'Optimal_v2' in new_features else 'Optimal'
                    if len(list(optimal_threshold.keys())) == 1:
                        threshold_key = list(optimal_threshold.keys())[0]

                        d["optimal"] = d.apply(lambda x: self.filter_optimal(x.Optimal_v2, optimal_threshold[threshold_key], threshold_key),  axis=1)

                        d.drop(optimal_col_name, inplace=True, axis=1)
                    elif len(optimal_threshold.keys()) == 2:
                        for key in list(optimal_threshold.keys()):
                            d["optimal_" + key] = d.apply(lambda x: self.filter_optimal(x.Optimal_v2, optimal_threshold[key], key),  axis=1)
                        d.drop(optimal_col_name, axis=1, inplace=True)

                    else: raise Exception("Please provide either one or two thresholds")
                    
                    new_features.remove(optimal_col_name)

                if compiling_features:
                    features.extend(new_features)
                    indicator_objs.extend(new_indicators)
                for span in spans:
                    new_features, new_inds = self.generateSpans(dataset=d, 
                                                indicator_name=span['indicator_name'],
                                                column_name=span['column_name'],
                                                param_name=span['param_name'],
                                                param_values=span['param_values'])
                    if compiling_features:
                        features.extend(new_features)
                        indicator_objs.extend(new_inds)
                coin_dataset.append(d)
                compiling_features = False

            coin_dataset = concat(coin_dataset)
            if scale:
                scaler = None
                if scale == 'minmax':
                    scaler = MinMaxScaler()

                elif scale == 'quartile':
                    scaler = QuantileTransformer(n_quantiles=100)
                elif scale == 'minmaxwindow':
                    realtimeScale(coin_dataset, features, minmaxwindowsize)
                else:
                    raise Exception(f'Unknown scaler: {scaler}')
                

                if coin_dataset.columns.to_series()[np.isinf(coin_dataset).any()] is not None:
                    for val in coin_dataset.columns.to_series()[np.isinf(coin_dataset).any()]:
                        if val in features:
                            features.remove(val)

                        coin_dataset[val].replace([np.inf], np.nan, inplace=True)
                        coin_dataset[val].replace([np.nan], coin_dataset[val].max(), inplace=True)
                if scaler:
                    coin_dataset[features] = scaler.fit_transform(coin_dataset[features])  

            dataset_list.append(coin_dataset)
            
        dataset = concat(dataset_list)
        dataset.reset_index(inplace=True, drop=True)
        dataset.dropna(inplace=True)
        return dataset, features, indicator_objs

    '''
    ARGS:
        -> models ([[model, String]]): list of model object-model name pairs
        -> scalers ([[scaler, String]]): list of scaler object-coin name pairs
        -> base_name (String): name of directory to write pickled model objects to
    RETURN:
        -> model_directory (String): path to newly created directory that models have been written to
        -> model_names ([String]): filenames for each model stored
        -> scaler_names ([String]): filenames for each scaler stored
    WHAT: 
        -> pickles passed models and scalers and creates a directory to save them to
    '''
    def saveModels(self, models, scalers, base_name):
        model_filenames = []
        scaler_filenames = []
        model_directory = f'./v2/strategy/saved_models/{base_name}/'
        try:
            os.mkdir(model_directory)
        except Exception as error:
            raise Exception(f'Error creating directory!')

        for model, model_name in models:
            name = f'model_{base_name}_{model_name}.sav'
            pickle.dump(model, open(f'{model_directory}{name}', 'wb'), protocol=pickle.HIGHEST_PROTOCOL)
            model_filenames.append(name)
        for scaler, coin_name in scalers:
            name = f'scaler_{base_name}_{coin_name}.sav'
            pickle.dump(scaler, open(f'{model_directory}{name}', 'wb'), protocol=pickle.HIGHEST_PROTOCOL)
            scaler_filenames.append(name)

        return model_directory, model_filenames, scaler_filenames


    '''
    ARGS:
        -> dataset (pandas Dataframe): dataset to eventually feed into the model
        -> split_size (float): size of the test size when splitting the train and test
        -> y_column_name (string): the name of the y column to set for the y train
        -> shuffle_data (bool): whether to shuffle the data
        -> balance_unbalanced_data (bool): whether to create balanced dataset from unbalanced data
        -> balance_info (dict): look at error message for propper formatting
    RETURN:
        -> (pandas Dataframe): trainX
        -> (pandas Dataframe): testX
        -> (pandas Dataframe): trainy
        -> (pandas Dataframe): testy
    WHAT: 
        -> wrapper for splitting up the data
    '''
    def splitData(self, dataset, split_size=0.2, y_column_name="Optimal_v2", shuffle_data=False, balance_unbalanced_data=False, balance_info={}):
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
            {'multiplier_val':4, 'superset_class_val':0, 'randomize_concat':True}")


    '''
    ARGS:
        -> y_dataset (numpy array): list of model object-model name pairs
    RETURN:
        -> (dict): weights of the different classes
    WHAT: 
        -> creates a dictionary with the weights of the classes for 
    '''
    def getWeights(self, y_dataset):
        weights = compute_class_weight('balanced', np.unique(y_dataset.values[:,0]), y_dataset.values[:,0])
        return {i : weights[i] for i in range(len(np.unique(y_dataset.values)))}


    '''
    ARGS:
        -> clf (model object): model for performing the predictions
        -> dataset (pandas Dataframe): dataset to feed into the model
        -> predict_proba (bool): should use the predict_proba method instead of just predict
        -> proba_thresh (float): threshold for when using the predict_proba
        -> plot_optimal (bool): plot the optimal along with the predicted
        -> optimal (numpy array): the optimal points so that they can be plotted along with 
    RETURN:
        -> (pandas Dataframe): data frame with the close and classify and possibly optimal points
    WHAT: 
        -> creates the predictions from the dataframe with the model
    '''
    def classifyPoints(self, clf, dataset, predict_proba=False, proba_thresh=0.7, plot_optimal=False, optimal=None, is_nn=False):
        classifyingDF = dataset.copy()
        if not is_nn:
            if not predict_proba:
                classifyingDF["classify"] = clf.predict(dataset.drop("close", axis=1).values)
            else:
                classifyingDF["predict"] = clf.predict_proba(dataset.drop("close", axis=1).values)[:,1]
                classifyingDF["classify"] = classifyingDF["predict"].apply(lambda x: self.filter_optimal(x, proba_thresh, "buy"))
                classifyingDF.drop("predict", axis=1, inplace=True)

            if plot_optimal:
                classifyingDF["optimal"] = optimal.values
                return classifyingDF[["close", "classify", "optimal"]]
        else:
            classifyingDF["predict"] = clf.predict_proba(dataset.drop("close", axis=1).values)[:,1]
            classifyingDF["classify"] = classifyingDF["predict"].apply(lambda x: self.filter_optimal(x, proba_thresh, "buy"))
            classifyingDF.drop("predict", axis=1, inplace=True)

            if plot_optimal:
                classifyingDF["optimal"] = optimal.values
                return classifyingDF[["close", "classify", "optimal"]]

        return classifyingDF[["close", "classify"]]


    """

    """
    def alterThreshold(self, new_thresh, model_name):
        version_str = ''
        base_path = './v2/strategy/saved_models/'
        model_dir = f'{base_path}{model_name}'
        if os.path.isdir(model_dir):
            highest_version = [0, 0]
            for f in [x for x in os.scandir(f'{model_dir}/')if x.is_dir()]:
                
                parts = f.name.split('_')
                version = int(parts[0])
                subversion = int(parts[1])
                if version == highest_version[0]:
                    if subversion > highest_version[1]:
                        highest_version = [version, subversion]
                elif version > highest_version[0]:
                    highest_version = [version, subversion]

            version_str = f'{highest_version[0]}_{highest_version[1] + 1}'

        model_dir = f'{model_dir}/{version_str}'
        model_dict = pickle.load(open(f'{model_dir}/{model_name}_{version_str}.sav', 'rb'))
        model_dict["proba_threshold"] = new_thresh
        pickle.dump(model_dict, open(f'{model_dir}/{model_name}_{version_str}.sav', 'wb'), protocol=pickle.HIGHEST_PROTOCOL)
    

    '''

    '''
    def graphPoints(self, df, mode="buy", plot_optimal=False):
        plt.clf()
        plt.figure(figsize=(20,10))

        color = "red" if mode == "buy" else "green"

        def inputPrice(row, column):
            if row.get(column) == 1:
                return row.close
            return np.nan

        df["classify"] = df.apply(lambda x: inputPrice(x, "classify"), axis=1)

        plt.scatter(df.index, df['classify'], color=color, s=50)

        if plot_optimal:
            df['optimal'] = df.apply(lambda x: inputPrice(x, 'optimal'), axis=1)
            
            plt.scatter(df.index, df['optimal'], color="purple")

        plt.plot(df.index, df['close'], color='blue')
        

    '''

    '''
    def testModel(self, model_name, version='latest', coin='UNI', num_processes=-1):
        trading_model = Trading(load_config('config.hjson'), get_data=False)
        trading_model.daisy_chain = True
        trading_model.currencies = [coin]
        trading_model.getDatasets()
        trading_model.plot = True
        trading_model.test_param_ranges = False
        trading_model.padding = 1000
        trading_model.freq = 1
        trading_model.strategies = [{
            'type': 'benchmark',
            'version': 'latest',
            'entry_models': [
                {
                    'name': model_name,
                    'version': version
                }
            ],
            'exit_models': []
        }]

        return trading_model.backtest(processes=num_processes)


    '''
    '''
    def exportModel(self, model, name, new_version, indicators, features, proba_threshold=0.0, is_nn=False):
        model_dict = dict()
        model_dict['indicators'] = indicators
        model_dict['features'] = features
        model_dict['proba_threshold'] = proba_threshold
        # check if name exists in saved_models directory -- if not we'll need to create a directory
        version_str = ''
        base_path = './v2/strategy/saved_models/'
        model_dir = f'{base_path}{name}'
        if os.path.isdir(model_dir):
            highest_version = [0, 0]
            for f in [x for x in os.scandir(f'{model_dir}/')if x.is_dir()]:
                
                parts = f.name.split('_')
                version = int(parts[0])
                subversion = int(parts[1])
                if version == highest_version[0]:
                    if subversion > highest_version[1]:
                        highest_version = [version, subversion]
                elif version > highest_version[0]:
                    highest_version = [version, subversion]
            
            if new_version:
                version_str = f'{highest_version[0] + 1}_0'
            else:
                version_str = f'{highest_version[0]}_{highest_version[1] + 1}'
            

        else:
            os.mkdir(model_dir)
            version_str = '1_0'
        model_dir = f'{model_dir}/{version_str}'
        os.mkdir(model_dir)
            

        if is_nn:
            model.save(f'{model_dir}/')
            model_dict['model'] = None
        else:
            model_dict['model'] = model

        pickle.dump(model_dict, open(f'{model_dir}/{name}_{version_str}.sav', 'wb'), protocol=pickle.HIGHEST_PROTOCOL)

        return version_str