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
import sys
if sys.version_info.minor < 8:
    import pickle5 as pickle
else:
    import pickle as pickle
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
import random

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
        for indicator, value, appended_name in indicator_list:
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
                ind_obj = indicator_object(_params=[], _value=value, _appended_name=appended_name)
                ind_obj.setDefaultParams()
                if ind_obj.name in param_specification:
                    params_to_set = findParams(ind_obj.params, param_specification[ind_obj.name].keys())
                    for p in params_to_set:
                        p.value = param_specification[ind_obj.name][p.name]
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
        inds_for_later = []
        for x in indicators:
            if x.value in dataset.columns:
                new_names = x.genData(dataset, gen_new_values=False)
                names.extend(new_names)
            else:
                inds_for_later.append(x)
        return names, inds_for_later


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
        inds_for_later = []
        for x in param_values:
            appended_name = f'{column_name}_{param_name}_{x}'
            # grab new instantiated indicator objects corresponding to each name passed, set the param accordingly
            ind = self.fetchIndicators([[indicator_name, column_name, appended_name]], param_specification={indicator_name + '_' + appended_name:{param_name: x}})[0]
            
            # generate the data and add it to the dataset
            inds.append(ind)
            if gen_data:
                if ind.value in dataset.columns:
                    names.extend(ind.genData(dataset, gen_new_values=False))
                else:
                    inds_for_later.append(ind)

        return names, inds, inds_for_later

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
        min_threshold = threshold[0]
        max_threshold = sys.maxsize
        if len(threshold) > 1:
            max_threshold = threshold[1]
        if mode == 'both':
            if optimal > min_threshold and optimal < max_threshold:
                return 1.0
            elif optimal < -1*min_threshold and optimal > -1 * max_threshold:
                return -1.0
            else:
                return 0.0
        elif mode == 'buy':
            if optimal > min_threshold and optimal < max_threshold:
                return 1.0
            else:
                return 0.0
        elif mode == "sell":
            if optimal < -1*min_threshold and optimal > -1 * max_threshold:
                return 1.0
            else:
                return 0.0
        else:
            raise ValueError("Did not provide either buy sell or both to the optimal_threshold dict")

    '''
    '''
    def filter_optimal_ensemble(self, optimal_arr, thresh_arr):
        if optimal_arr.predict0 > thresh_arr[0] and optimal_arr.predict1 > thresh_arr[1]:
            return 1.0
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
    def loadData(self, indicators, param_spec={}, optimal_threshold={"buy":(0.01, 0.05)}, spans={}, test=False, test_coin='BTC', test_freq=1, scale='', minmaxwindowsize=15000, seperate_by_coin=False):
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
                
                new_features, inds_for_later = self.genDataForAll(dataset=d, indicators=new_indicators)
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
                    new_features, new_inds, inds_later = self.generateSpans(dataset=d, 
                                                indicator_name=span['indicator_name'],
                                                column_name=span['column_name'],
                                                param_name=span['param_name'],
                                                param_values=span['param_values'])
                    inds_for_later.extend(inds_later)
                    if compiling_features:
                        features.extend(new_features)
                        indicator_objs.extend(new_inds)
                while inds_for_later:
                    new_features, inds_for_later = self.genDataForAll(dataset=d, indicators=inds_for_later)
                    if compiling_features:
                        features.extend(new_features)
                        

                
                if scale:
                    scaler = None
                    if scale == 'minmax':
                        scaler = MinMaxScaler()

                    elif scale == 'quartile':
                        scaler = QuantileTransformer(n_quantiles=100)
                    elif scale == 'minmaxwindow':
                        realtimeScale(d, features, minmaxwindowsize)
                    else:
                        raise Exception(f'Unknown scaler: {scaler}')
                    

                    if d.columns.to_series()[np.isinf(d).any()] is not None:
                        for val in d.columns.to_series()[np.isinf(d).any()]:
                            if val in features:
                                features.remove(val)

                            d[val].replace([np.inf], np.nan, inplace=True)
                            d[val].replace([np.nan], dataset[val].max(), inplace=True)
                    if scaler:
                        d[features] = scaler.fit_transform(d[features]) 

                coin_dataset.append(d)
                compiling_features = False

            coin_dataset = concat(coin_dataset)
            coin_dataset.reset_index(inplace=True, drop=True)
            coin_dataset.dropna(inplace=True)

            dataset_list.append(coin_dataset)
        
        if not seperate_by_coin:
            dataset = concat(dataset_list)
            dataset.reset_index(inplace=True, drop=True)
            dataset.dropna(inplace=True)
            return dataset, features, indicator_objs
        else:
            return dataset_list, features, indicator_objs

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
    def classifyPoints(self, clf_list, dataset, predict_proba=False, proba_thresh=[0.7], plot_optimal=False, optimal=None, is_nn=False):
        classifyingDF = dataset.copy()
        if len(clf_list) == 1:
            clf = clf_list[0]
            proba_thresh = proba_thresh[0]

            if is_nn or predict_proba:
                if is_nn:
                    classifyingDF["predict"] = clf.predict(dataset.drop("close", axis=1).values)[:,1]
                else:
                    classifyingDF["predict"] = clf.predict_proba(dataset.drop("close", axis=1).values)[:,1]

                classifyingDF["classify"] = classifyingDF["predict"].apply(lambda x: self.filter_optimal(x, (proba_thresh,), "buy"))
                classifyingDF.drop("predict", axis=1, inplace=True)

            else:
                classifyingDF["classify"] = clf.predict(dataset.drop("close", axis=1).values)

        elif len(clf_list) == 2:
            clf0 = clf_list[0]
            clf1 = clf_list[1]

            if is_nn or predict_proba:
                if is_nn:
                    classifyingDF['predict0'] = clf0.predict(dataset.drop("close", axis=1).values)[:,1]
                    classifyingDF['predict1'] = clf1.predict(dataset.drop("close", axis=1).values)[:,1]
                else:
                    classifyingDF['predict0'] = clf0.predict_proba(dataset.drop("close", axis=1).values)[:,1]
                    classifyingDF['predict1'] = clf1.predict_proba(dataset.drop("close", axis=1).values)[:,1]

                classifyingDF["classify"] = classifyingDF.apply(lambda x: self.filter_optimal_ensemble(x, proba_thresh), axis=1)
                classifyingDF.drop(["predict0", 'predict1'], axis=1, inplace=True)
            else:
                classifyingDF['class0'] = clf0.predict(dataset.drop('close', axis=1).values)
                classifyingDF['class1'] = clf1.predict(dataset.drop('close', axis=1).values)

                classifyingDF["classify"] = classifyingDF[["class0", 'class1']].any(1).astype(int)
                classifyingDF.drop(["class0", "class1"], axis=1, inplace=True)
        else:
            raise Exception("We haven't added for more than one ensemble you code it if you want to try it")

        if plot_optimal:
            classifyingDF["optimal"] = optimal.values
            return classifyingDF[["close", "classify", "optimal"]]

        return classifyingDF[["close", "classify"]]


    '''
    ARGS:
        -> new_thresh (Float): new probability threshold for the given model
        -> model_name (String): name of model to alter
    RETURN:
        -> None
    WHAT: 
        -> Alters the probability threshold for the latest version of a given model
    TODO:
        -> test this
        -> add the ability to change a specific model version
    '''
    def alterThreshold(self, new_thresh, model_name):
        version_str = ''
        base_path = './v2/strategy/saved_models/'
        model_dir = f'{base_path}{model_name}'

        # get the latest version of the model
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

        # load the model, change the probability threshold, and save it again
        model_dir = f'{model_dir}/{version_str}'
        model_dict = pickle.load(open(f'{model_dir}/{model_name}_{version_str}.sav', 'rb'))
        model_dict["proba_threshold"] = new_thresh
        pickle.dump(model_dict, open(f'{model_dir}/{model_name}_{version_str}.sav', 'wb'), protocol=pickle.HIGHEST_PROTOCOL)
    

    '''
    ARGS:
        -> df (Dataframe): dataframe to plot points for
        -> mode (String): should be either 'buy' or 'sell' and specifies whether buy or sell points are plotted
        -> plot_optimal (Bool): whether or not to plot the optimal buy/sell points as well
    RETURN:
        -> None
    WHAT: 
        -> Plots the dataframe's buy or sell points alongside the close price
        -> optionally plots the label data (optimal buy/sell points) for reference
    '''
    def graphPoints(self, df, mode="buy", plot_optimal=False, plot_sma=False, fields=[]):
        plt.clf()
        plt.figure(figsize=(20,10))

        color = "red" if mode == "buy" else "green"

        def inputPrice(row, column):
            if row.get(column) == 1:
                return row.close
            return np.nan

        # plot the classification buy/sell points
        df["classify"] = df.apply(lambda x: inputPrice(x, "classify"), axis=1)
        if plot_sma:
            df["plot_sma_short"] = df.iloc[:,1].rolling(window=30).mean()
            plt.plot(df.index, df['plot_sma_short'], color="orange")
            plt.plot(df.index, df['plot_sma_short']*0.99, color="yellow")
            plt.plot(df.index, df['plot_sma_short']*0.98, color="red")
            plt.plot(df.index, df['plot_sma_short']*0.97, color="pink")
            df["plot_sma_long"] = df.iloc[:,1].rolling(window=90).mean()
            plt.plot(df.index, df['plot_sma_long'], color="brown")
            plt.plot(df.index, df['plot_sma_long']*0.99, color="green")
            plt.plot(df.index, df['plot_sma_long']*0.98, color="blue")
            plt.plot(df.index, df['plot_sma_long']*0.97, color="purple")
        
        plt.scatter(df.index, df['classify'], color=color, s=50)

        # plot the optimal buy/sell points
        if plot_optimal:
            df['optimal'] = df.apply(lambda x: inputPrice(x, 'optimal'), axis=1)
            
            plt.scatter(df.index, df['optimal'], color="purple")
        for x in fields:
            
            
            plt.plot(df.index, df[x], color=np.random.rand(3,))
        # plot the close price
        plt.plot(df.index, df['close'], color='black')
        

    '''
    ARGS:
        -> model_name (String): name of model to test
        -> version (String): version of model to test
        -> coin (String): coin to test the model on 
        -> num_processes (Int): number of processes to allow backtest() to use
    RETURN:
        -> score, entries, exits (Int, [(Int,  Int)], [(Int,  Int)]): 
            -> overall ending cash value of portfolio
            -> list of timestamp, coin value pairs for entries
            -> list of timestamp, coin value pairs for exits
    WHAT: 
        -> Backtests the given model version on the given coin and returns the results
    '''
    def testModel(self, model_name, version='latest', coin='UNI', num_processes=-1):
        # we need to altar the config prior to loading the data, so set get_data to False
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
    ARGS:
        -> model (Model object): object holding an ML model
        -> name (String): name to save the model as
        -> new_version (Bool): whether or not to save the model as a new base version 
            -> otherwise will be saved as a new subversion
        -> indicators ([Indicator]): list of Indicator objects necessary to generate the features necessary as input for the model
        -> features ([String]): ordered list of feature names that the model takes as input
        -> proba_threshold (Float): the threshold value to accept classifications above (if this is a classifier and should use predict_proba)
            -> if this is not important, an input of 0.0 (default) will not be considered
        -> is_nn (Bool): whether or not the model is a nueral network (requires different import procedure)
    RETURN:
        -> version_str (String): the verison that the new model was saved as
    WHAT: 
        -> Saves a model to the 'saved_models' directory
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

    def exportProductionModel(self, model, model_type, name, new_version, indicators, features, proba_threshold=0.0, is_nn=False):
        model_dict = dict()
        model_dict['proba_threshold'] = proba_threshold
        model_dict['model_type'] = model_type
        model_dict['features'] = features    
        version_str = ''
        base_path = './production_models/'
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
        # we need to package all the information needed to construct the appropriate indicator object
        # since we cannot send the indicator itself
        # this includes:
        # -> name
        # -> type of indicator
        # -> params
        # -> value (what it's being computed upon)
        # it's necessary to send all of this information, as indicators constructed for a model can be highly coupled
        # we need this to work exactly the same way in beverly hills
        # rather than rely on defaults in beverly hills, we can just send the information stored in the object
        # since beverly hills is not really an environment for development
        indicator_dict = dict()
        for ind in indicators:
            indicator_dict[ind.name] = dict()
            # package params
            indicator_dict[ind.name]['params'] = dict()
            for param in ind.params:
                indicator_dict[ind.name]['params'][param.name] = param.value
            # store value
            indicator_dict[ind.name]['value'] = ind.value
            # store indicator type (class)
            indicator_dict[ind.name]['type'] = type(ind).__name__
        model_dict['indicators'] = indicator_dict

        if is_nn:
            model.save(f'{model_dir}/')
            model_dict['model'] = None
        else:
            model_dict['model'] = model

        pickle.dump(model_dict, open(f'{model_dir}/{name}_{version_str}.sav', 'wb'), protocol=pickle.HIGHEST_PROTOCOL)

        return version_str

    def multiProcessSimulateData(self, datasets, strat_obj):
        process_pool = mp.Pool(mp.cpu_count())
        params = zip(datasets, repeat(strat_obj))
        datasets = process_pool.starmap(self.simulate_all_trades, params)
        process_pool.close()
        dataset = pd.concat(datasets)
        return dataset

    def simulate_all_trades(self, dataset, strategy):
        dataset['is_potential_buy'] = False
        coin = 'COIN'
        generic_strategy = strategy([coin])
        opened_trades = dict()
        closed_trades = dict()
        for row in dataset.itertuples():
            otkeys = list(opened_trades.keys())
            for tick in otkeys:
                opened_trades[tick][0].process(row, coin)
                if opened_trades[tick][0].calc_exit(row, coin):
                    closed_trades[tick] = (row.close/opened_trades[tick][1]) - 1
                    del opened_trades[tick]
            if generic_strategy.calc_entry(row, coin):
                dataset.loc[(dataset.time == row.time),'is_potential_buy']=True
                opened_trades[row.time] = (generic_strategy, row.close)
                generic_strategy = strategy([coin])
            
        dataset['simul_profit'] = 0.0
        for k in closed_trades:
            dataset.loc[(dataset.time == k),'simul_profit']=closed_trades[k]
        return dataset

    def importModel(self, model, version="latest", is_entry=True):
        #get the correct model
        base_dir = './v2/strategy/saved_models/' + model + '/'

        if version == 'latest': # fetch the latest version of the given strategy
            all_files = os.listdir(base_dir)
            highest_version = [0, 0]

            for f in [x for x in os.scandir(f'{base_dir}/')if x.is_dir()]:
                parts = f.name.split('_')
                version = int(parts[0])
                subversion = int(parts[1])
                if version == highest_version[0]:
                    if subversion > highest_version[1]:
                        highest_version = [version, subversion]
                elif version > highest_version[0]:
                    highest_version = [version, subversion]
                    
            # set version to be the highest version found
            version = f'{highest_version[0]}_{highest_version[1]}'
        
        # this code attempts to find the module (strategy) with the given name, 
        # and gets the corresponding object if it exists
        full_path = base_dir + version + '/' + model + '_' + version + '.sav'
        
        model_data = pickle.load(open(full_path, 'rb'))

        if not model_data["model"]: #means its a neural net and we need to load w/ keras
            model_path = "/".join(full_path.split("/")[:-1])
            model_data["model"] = keras.models.load_model(model_path)


        return model_data
        