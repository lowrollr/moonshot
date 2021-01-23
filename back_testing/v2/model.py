'''
FILE: model.py
AUTHORS:
    -> Jacob Marshall (marshingjay@gmail.com)
    -> Ross Copeland (rhcopeland101@gmail.com)
WHAT:
    -> This file contains the Trading class and its member functions,
    which implement all core functionaltiy of the backtesting framework
'''
import warnings
warnings.simplefilter(action='ignore')

import pandas as pd
import os
import sys
import time
import importlib
import inspect
import random
from math import sqrt
import plotly.graph_objs as go
from plotly.offline import plot
from collections import deque
import matplotlib.pyplot as plt
from tqdm import tqdm
from itertools import product, takewhile
import random
import numpy as np
from multiprocessing import Pool, cpu_count
from alive_progress import alive_bar

from v2.strategy.strategies.strategy import Strategy
from v2.report import write_report, writePMReport
import v2.utils as utils
from load_config import load_config
from v2.multiprocess import Multiprocess

'''
CLASS: Trading
WHAT:
    -> The Trading class is a wrapper for an instance of the backtesting infrastructure
    -> Everything that's a core process of backtesting goes in here
'''
class Trading:

    '''
    ARGS:
        -> config ({String: String}): param-value pairs read in from 'config.config' file
    RETURN:
        -> None
    WHAT: 
        -> initializes and configures the Trading class using the values read in from the config file
    '''
    def __init__(self, config, get_data=True):
        
        # Ensure logging/plotting directories are set up correctly
        utils.checkLogPlotDir()

        # We need to read in the fields from our config file and turn them into actionable parameters
        # Parse each field as needed and construct the proper paremeters
        self.currencies = config['currencies']
        self.daisy_chain = config['daisy_chain']
        self.chunk_ids = config['chunk_ids']
        self.freq = config['freq']
        self.fees = float(config['fees'])
        self.indicators_to_graph = config['indicators_to_graph']
        self.strategies = config['strategies']
        self.timespan = []
        self.slippage = float(config["slippage"])
        self.report_format = config['report_format']
        self.data_source = config['data_source']
        self.scale = config['scale']
        self.padding = config['padding']
        if config['timespan'] == 'max': # test over entire dataset
            self.timespan = [0, sys.maxsize]
        elif '.' in config["timespan"][0]:  # test from date_a to date_b military time (yyyy.mm.dd.hh.mm)
            self.timespan = utils.convertTimespan(config["timespan"])
        elif len(config['timespan']) == 1: # date_a already defined in unix time, no need to convert
            self.timespan = [int(config['timespan'][0]), sys.maxsize]
        else: 
            self.timespan = [int(x) for x in config['timespan']]
        
        
        self.test_param_ranges = config['test_param_ranges'] 
        
        self.plot = config['plot']
        self.df_groups = []
        # Load the appropriate datasets for each currency pair 
        # This happens last, depend on other config parameters
        if get_data:
            self.getDatasets()


    '''
    ARGS:
        -> None
    RETURN:
        -> None
    WHAT: 
        -> fetches groups of datasets for each currency and stores it in the class's list of dataset groups
    TODO:
        -> fix retrieve all to account for dataset refactor
    '''
    def getDatasets(self):
        
        if self.currencies == ['all']:
            pass
            # filenames = utils.retrieveAll(freq)
        else:
            for i,b in enumerate(self.currencies):
                cur_group = []
                b_dir = f'historical_data/{self.data_source}/{b}/{self.freq}m/'
                files = os.listdir(b_dir)
                # if daisy chaining is enabled, append all datasets for the given currency to the group list
                if self.daisy_chain:
                    for j,f in enumerate(sorted(files)):
                        b_file = f'{b_dir}{f}'
                        my_df = pd.read_csv(b_file)
                        my_df = my_df[['close_time', 'high', 'low', 'close', 'open', 'volume']]
                        my_df.rename(columns={'close_time': 'time'}, inplace=True)
                        my_df = my_df[(my_df['time'] > self.timespan[0]) & (my_df['time'] < self.timespan[1])]
                        if not my_df.empty:
                            cur_group.append(my_df)
                # otherwise, find the specified chunk in the config file and add the single dataframe corresponding to that chunk to the group list
                else:
                    try:
                        # construct the appropriate filename to fetch given a chunk id and frequency
                        zero_str = '0'
                        b_file = f'{b_dir}{b}USDT-{self.freq}m-data_chunk{zero_str * (6 - len(str(self.chunk_ids[i])))}{self.chunk_ids[i]}.csv'
                        my_df = pd.read_csv(b_file)
                        # grab the appropriate columns
                        my_df = my_df[['close_time', 'high', 'low', 'close', 'open', 'volume']]
                        # this will need to be adapted to other datasets (other than binance), probably should standardize how we pass dataframes in but this is fine for now
                        my_df.rename(columns={'close_time': 'time'}, inplace=True)
                        my_df = my_df[(my_df['time'] > self.timespan[0]) & (my_df['time'] < self.timespan[1])]
                        if not my_df.empty:
                            cur_group.append(my_df)
                    except Exception:
                        # will be raised if the chunk id given in the config file doesn't exist
                        raise Exception(f"The specified chunk ({self.chunk_ids[i]}) for {b} does not exist!\n")
                
                if cur_group:
                    # append the group to the master group list, paired with the dataset name
                    self.df_groups.append([cur_group, b])
                


    '''
    ARGS:
        -> strategy (String): name of the strategy to import
        -> version (String): version of the strategy to import
    RETURN:
        -> obj (Strategy): Strategy object, or None if the given strategy name does
            not correspond to a strategy
    WHAT: 
        -> finds the object corresponding to the given strategy and version number in the strategies
            directory, returns a reference(?) to that object which can be used to call the constructor
    '''
    def importStrategy(self, strategy):
        # construct the base directory
        base_module = 'v2.strategy.strategies.' + strategy['type']

        if strategy['version'] == 'latest': # fetch the latest version of the given strategy
            base_dir = './v2/strategy/strategies/' + strategy['type']
            highest_version = [0,0]
            # find the highest version number
            for f in [x for x in os.scandir(f'{base_dir}/')]:
                if f.name[0:len(strategy['type'])] == strategy['type']:
                    my_file = f.name.split('.py')[0]
                    my_version = my_file.split('_v')[1]
                    parts = my_version.split('_')
                    version = int(parts[0])
                    subversion = int(parts[1])
                    if version == highest_version[0]:
                        if subversion > highest_version[1]:
                            highest_version = [version, subversion]
                    elif version > highest_version[0]:
                        highest_version = [version, subversion]
                    
            # set version to be the highest version found
            version = f'{highest_version[0]}_{highest_version[1]}'
        else:
            version = strategy['version']
        
        # this code attempts to find the module (strategy) with the given name, 
        # and gets the corresponding object if it exists
        module = importlib.import_module(base_module + '.' + strategy['type'] + '_v' + version)
        for mod in dir(module):
            obj = getattr(module, mod)
            if inspect.isclass(obj) and issubclass(obj, Strategy) and obj != Strategy:
                return obj

        # return None if no object is found
        return None
    
        
    '''
    ARGS:
        -> strategy (Strategy): Strategy object (to call it's entry, exit, and process function)
        -> my_dataset ((Dataframe, String)): dataset to run the strategy on, and its name
        -> *args[0] (String) <Optional>: param names to append to log file (if it's useful to specify)
    RETURN:
        -> conv_position (Float): Total amount of funds in quote currency held after executing the 
            strategy on the dataset
        -> entries ((Int, Float)): tuples (time, value) pretaining to when a position was entered
        -> exits ((Int, Float)): tuples (time, value) pretaining to when a position was exited
    WHAT: 
        -> Executes the given strategy on the dataset group
        -> Calls the appropriate strategy procedures each tick
            i.e. calc_enrty() when looking to enter
                 calc_exit() when looking to exit
                 process() every tick
        -> This assumes that our entire position is converted from currency a to currency b and
            vice-versa when making a trade
        -> Sends trade statistics to the reporting module so a report can be generated
        -> Concatenates all dataset chunks in dataset group but ensures trades do not occur between chunks
    TODO:
        -> Is slippage all the way implemented?
    '''
    def executeStrategy(self, strategy, dataset, first_times, dataset_name, should_print=True, plot=True, *args):
        # remove the first x rows equal to the amount of padding specified
        dataset = dataset[self.padding:]

        # initialize starting position to 1000000 units
        position_quote = 1000000.00
        account_value = position_quote
        start = position_quote
        # initialize base position to 0 units
        position_base = 0.00

        # this will keep track of whether or not we are engaged in a position in the base currency
        position_taken = False
        
        
        
        # this keeps track of fees we incur by entering a postion in the base currency
        # these will be subtracted once we have converted our position back to the quote currency
        # (by closing our position or reaching the end of the dataset)
        inc_fees = 0.0

        # keeps track of the current close price (used within the loop as well as after)
        close = 0.0

        # keeps track of the last quote position we were engaged in (useful for backtracking to last quote position when reached end of time window)
        old_quote = 0.0
        
        # keep track of slippage
        slippage_tot = 0.0
        slippage_pos_base = 0.00
        slippage_pos_quote = position_quote
        slippage_fees = 0.0

        # stores tuples (time, value) for when we enter/exit a position
        # these get plotted
        entries = []
        exits = []
        account_history = []


        starting_base_value = dataset['close'].values[0]
        # grab all the rows in the dataset as Series objects
        rows = dataset.itertuples()
        with alive_bar(len(dataset), spinner=utils.getRandomSpinner()) as bar:

            # execute the strategy row by row (tick by tick)
            for row in rows:
                bar()
                # if we are currently in a position in the base currency and reach the end of the chunk, revert to our last quote position
                # if not position_quote and row.time in first_times:
                #     position_quote = old_quote
                #     position_base = 0.0
                #     # remove the last entry so entries/exits stay paired up
                #     entries.pop()
                #     position_taken = False

                # keep track of the close price for the given tick
                close = row.close
                slippage_close = close

                # run the process function (will execute anything that needs to happen each tick for the strategy)
                strategy.process(row, dataset_name)
                if position_quote:
                    account_value = position_quote
                else:
                    account_value = position_base * close
                account_history.append(account_value)
                if not position_taken: # if we are not entered into a position

                    # run the entry function for our strategy
                    if strategy.calc_entry(row, dataset_name):
                        # if the entry function returns True, it is signaling to enter, so take a position
                        position_taken = True

                        # calculate fees that will be incurred
                        inc_fees = position_quote * self.fees

                        # convert our position to the base currency
                        old_quote = position_quote
                        position_base = position_quote / close
                        position_quote = 0.0

                        # append entry to entries log for the graph as well as to the text log
                        entries.append([row.time, close])
                        
                        # # do slippage things if we are keeping track of slippage
                        # if self.slippage != 0:
                        #     slippage_fees = slippage_pos_quote * self.fees
                        #     slippage_close = utils.add_slippage("pos", close, self.slippage)
                        #     slippage_log.append(str(row.time) + ': bought at ' + str(slippage_close) + " tried to buy at " + str(close))
                        #     slippage_pos_base = slippage_pos_quote / slippage_close
                        #     slippage_tot += close - slippage_close
                        #     slippage_pos_quote = 0.0
                    
                    
                else: # otherwise, we are looking to exit a position
                    
                    # run the exit function of our strategy
                    if strategy.calc_exit(row, dataset_name):
                        # if the exit function returns True, it is signaling to exit, so leave the position
                        position_taken = False

                        # convert our position to the quote currency
                        position_quote = position_base * close
                        position_base = 0.0

                        # subtract fees from this transaction as well as the fees from our entry transaction
                        position_quote = position_quote * (1 - self.fees)
                        position_quote -= inc_fees
                        delta = position_quote - old_quote

                        # append exit to exits log for the graph as well as to the text log
                        exits.append([row.time, close])

                        # # do slippage things if we are keeping track of slippage
                        # if self.slippage != 0:
                        #     slippage_close = utils.add_slippage("neg", close, self.slippage)
                        #     slippage_pos_quote = slippage_pos_base * slippage_close
                        #     slippage_pos_quote = slippage_pos_quote * (1 - self.fees)
                        #     slippage_pos_quote -= slippage_fees
                        #     slippage_tot += slippage_close - close
                        #     slippage_pos_base = 0.0
                        #     slippage_log.append(str(row.time) + ": sold at " + str(slippage_close) + " tried to sell at " + str(close))
                
        dataset['account_value'] = np.array(account_history)

        ending_value = close
        
        # build the file name to use for graphs/plots
        name = 'results-' + strategy.name + '-' + dataset_name

        # append the param string if it was passed
        if args:
            name += '-' + args[0]

        # convert our position to the quote price if it isn't already in the quote price
        conv_position = position_quote
        if position_base:
            conv_position = (position_base * close) * (1 - self.fees)

        # compute slippage
        # slippage_conv_pos = slippage_pos_quote
        # if self.slippage != 0:
        #     slippage_close = utils.add_slippage("neg", close, self.slippage)
        #     slippage_conv_pos = (slippage_pos_base * slippage_close) * (1 - self.fees)

        # std_dev = utils.getLogStd(log)
        
        # write stats to dict to send to reports
        stats = dict()
        stats['Initial Portfolio Value'] = 1000000.00
        stats['Exit Portfolio Value'] = round(conv_position, 2)
        stats['Portfolio RateOfChange ($)'] = round(conv_position - start, 2)
        stats['Portfolio RateOfChange (%)'] = str(round(((conv_position / start) * 100) - 100, 2)) + '%'
        stats['Initial Asset Value'] = starting_base_value
        stats['Final Asset Value'] = ending_value
        stats['Asset Growth ($)'] = round(ending_value - starting_base_value, 2)
        stats['Asset Growth (%)'] = str(round(((ending_value / starting_base_value) * 100) - 100, 2)) + '%'

        # write the report
        if plot:
            print('Generating Report...')
            write_report(dataset, entries, exits, self.indicators_to_graph, name, self.report_format, stats, self.fees)

        # return the final quote position, as well as the list of entries and exits
        return conv_position, entries, exits
    

    def executePM(self, coin_datasets, start_times, strategy, allocation_mode='aggressive', should_print=True, plot=True):
        coin_times = dict()
        all_timestamps = []
        coins = []
        datasets = dict()

        cash = 1000000.00
        entries = dict()
        exits = dict()
        weights = dict()
        coin_allocations = dict()
        portfolio_value = []
        
        for name, dataset in coin_datasets:
            coins.append(name)
            datasets[name] = dataset
            coin_times[name] = dict()
            for row in dataset.itertuples():
                coin_times[name][row.time] = row.Index
            all_timestamps.extend(list(coin_times[name].keys()))
        all_timestamps = sorted(list(set(all_timestamps)))
        coin_info = dict()
        for coin in coins:
            coin_info[coin] = dict()
            coin_info[coin]['last_close_price'] = 0.0
            coin_info[coin]['in_position'] = False
            coin_info[coin]['enter_value'] = 0.0
            coin_info[coin]['cash_invested'] = 0.0
            coin_info[coin]['weight'] = 1/len(coins)
            coin_info[coin]['last_start_time'] = 0
            coin_info[coin]['recent_trade_results'] = deque(maxlen=10)
            coin_info[coin]['allocation'] = 0.0
            # coin_info[coin]['frozen'] = False

            entries[coin] = []
            exits[coin] = []
            weights[coin] = []
            coin_allocations[coin] = []

        coin_allocations['CASH'] = [(all_timestamps[0], 1.0)]
        cash_allocation = 1.0
        
        

        with alive_bar(len(all_timestamps), spinner=utils.getRandomSpinner()) as bar:
            for time in all_timestamps:
                enter_signals = []
                exited_position = False
                
                # get enter/exit signals from coins
                for coin in coins:
                    if time in coin_times[coin]:
                        time_index = coin_times[coin][time]
                        
                        row = datasets[coin].iloc[time_index]
                        
                        coin_info[coin]['last_close_price'] = row.close
                        strategy.process(row, coin)

                        if not coin_info[coin]['in_position']:
                            
                            if strategy.calc_entry(row, coin):
                                enter_signals.append(coin)

                        else:
                            if time in start_times:
                                # coin_info[coin]['in_position'] = False
                                # cash += coin_info[coin]['cash_invested'] * (1 + self.fees)
                                pass

                            if strategy.calc_exit(row, coin):
                                coin_info[coin]['in_position'] = False
                                exits[coin].append((row.time, row.close))
                                exited_position = True
                                new_cash_value = (1-self.fees)*((coin_info[coin]['cash_invested'] / coin_info[coin]['enter_value']) * row.close)
                                profit = (new_cash_value / ((coin_info[coin]['cash_invested'] * (1 + self.fees)))) - 1
                                coin_info[coin]['recent_trade_results'].append((profit, (coin_info[coin]['last_start_time'], row.time)))
                                coin_info[coin]['cash_invested'] = 0.0
                                cash += new_cash_value

                
                # positions = [coin_info[coin]['last_close_price']/coin_info[coin]['enter_value'] - 1 < -0.05 for coin in coin_info if coin_info[coin]['in_position']]
                # if positions and sum(positions)/len(positions) > 0.5:
                    
                #     for coin in coin_info:
                #         coin_info[coin]['frozen'] = True
                #         if coin_info[coin]['in_position']:
                        
                #             coin_info[coin]['in_position'] = False
                #             exits[coin].append((time, coin_info[coin]['last_close_price']))
                #             new_cash_value = (1-self.fees)*((coin_info[coin]['cash_invested'] / coin_info[coin]['enter_value']) * coin_info[coin]['last_close_price'])
                #             profit = (new_cash_value / ((coin_info[coin]['cash_invested'] * (1 + self.fees)))) - 1
                #             coin_info[coin]['recent_trade_results'].clear()
                #             coin_info[coin]['cash_invested'] = 0.0
                #             cash += new_cash_value
                

                            
                if enter_signals:
                    # process enter signals
                    if allocation_mode == 'conservative':
                        weight_sum = sum([coin_info[x]['weight'] for x in coin_info if not coin_info[x]['in_position']])
                        
                        for coin in enter_signals:
                            enter_cash = cash * (coin_info[coin]['weight'] / weight_sum)
                            cash -= enter_cash
                            weight_sum -= coin_info[coin]['weight']
                            coin_info[coin]['cash_invested'] = enter_cash * (1 - self.fees)
                            coin_info[coin]['enter_value'] = coin_info[coin]['last_close_price']
                            coin_info[coin]['in_position'] = True
                            entries[coin].append((time, coin_info[coin]['last_close_price']))
                            coin_info[coin]['last_start_time'] = time
                        
                        
                        
                    elif allocation_mode == 'aggressive':
                        weight_sum = sum([coin_info[x]['weight'] for x in coin_info if not coin_info[x]['in_position']])
                        coin_weight_pairs = sorted([(coin, coin_info[coin]['weight']) for coin in enter_signals], key=lambda k: k[1], reverse=True)
                        
                        num_coins =  len([x for x in coin_info if coin_info[x]['last_close_price']])
                        total_coins = len(coin_info)
                        for coin, weight in coin_weight_pairs:
                            
                            allocation = min(0.50, ((3*total_coins)/num_coins) * weight)
                            # if coin_info[coin]['frozen']:
                            #     allocation = min(allocation, 0.005)
                            if cash and allocation <= weight_sum :
                                enter_cash = cash * (allocation / weight_sum)
                                cash -= enter_cash
                                weight_sum -= coin_info[coin]['weight']
                                coin_info[coin]['cash_invested'] = enter_cash * (1 - self.fees)
                                coin_info[coin]['enter_value'] = coin_info[coin]['last_close_price']
                                coin_info[coin]['in_position'] = True
                                entries[coin].append((time, coin_info[coin]['last_close_price']))
                                coin_info[coin]['last_start_time'] = time
                            else:
                                
                                current_positions = sorted([(c, (coin_info[c]['last_close_price'] - coin_info[c]['enter_value'])/coin_info[c]['last_close_price']) for c in coin_info if coin_info[c]['in_position']], key=lambda x:x[1], reverse=True)
                                # current_positions = sorted([(c, time - coin_info[c]['last_start_time']) for c in coin_info if coin_info[c]['in_position']], key=lambda x:x[1], reverse=True)
                                for coin_c, profit in current_positions:
                                    if profit > -0.02:
                                        if time <= coin_info[coin_c]['last_start_time']+5:
                                            continue
                                        if cash and allocation <= weight_sum:
                                            break
                                        cash_needed = (cash * (allocation / weight_sum)) - cash
                                        cash_available = (1-self.fees)*((coin_info[coin_c]['cash_invested'] / coin_info[coin_c]['enter_value']) * coin_info[coin_c]['last_close_price'])
                                        # if the amount of cash we need to open the position exceeds the amount of cash available in position i, 
                                        if not cash or cash_needed >= cash_available * (1/2):
                                            coin_info[coin_c]['in_position'] = False
                                            exited_position = True
                                            exits[coin_c].append((time, coin_info[coin_c]['last_close_price']))
                                            new_cash_value = (1-self.fees)*((coin_info[coin_c]['cash_invested'] / coin_info[coin_c]['enter_value']) * coin_info[coin_c]['last_close_price'])
                                            profit = (new_cash_value / ((coin_info[coin_c]['cash_invested'] * (1 + self.fees)))) - 1
                                            coin_info[coin_c]['recent_trade_results'].append((profit, (coin_info[coin_c]['last_start_time'], time)))
                                            coin_info[coin_c]['cash_invested'] = 0.0
                                            cash += new_cash_value
                                            weight_sum += coin_info[coin_c]['weight']
                                    else:
                                        # partially close the position, but keep the reamining capital that's not needed in the position
                                        coin_info[coin_c]['cash_invested'] = (cash_available - cash_needed) / (1 - self.fees)
                                        cash += cash_needed
                                        weight_sum = allocation
                                
                                        
                                # sanity check with if statement 
                                if allocation <= weight_sum:
                                    # open the new position
                                    enter_cash = cash * (allocation / weight_sum)
                                    cash -= enter_cash
                                    weight_sum -= coin_info[coin]['weight']
                                    coin_info[coin]['cash_invested'] = enter_cash * (1 - self.fees)
                                    coin_info[coin]['enter_value'] = coin_info[coin]['last_close_price']
                                    entries[coin].append((time, coin_info[coin]['last_close_price']))
                                    coin_info[coin]['in_position'] = True
                                    coin_info[coin]['last_start_time'] = time
                
                    


                # update weights
                if exited_position:
                    scores = []
                    for coin in coins:
                        if coin_info[coin]['recent_trade_results']:
                            trade_results = [x[0] for x in coin_info[coin]['recent_trade_results']]
                            avg_profit = sum(trade_results)/len(coin_info[coin]['recent_trade_results'])
                            
                            # max_hold_time = max([(x[1][1] - x[1][0])/ 60000 for x in coin_info[coin]['recent_trade_results']])
                            # if coin_info[coin]['frozen'] and len(coin_info[coin]['recent_trade_results']) >= 2 and avg_profit > 0.5:
                            #     coin_info[coin]['frozen'] = False
                            scores.append(avg_profit)
                        else:
                            scores.append(-1.0)
                        
                   
                    
                    min_value = min(score for score in scores if score != -1.0)
                    if min_value < 0:
                        scores = [x + abs(min_value) if x != -1.0 else -1.0 for x in scores ]
                    scores = [np.median([y for y in scores if y != -1.0]) if x == -1.0 else x for x in scores ]
                    scores_sum = sum(scores)
                    if scores_sum:
                        scores = [x / scores_sum for x in scores]
                    else:
                        scores = [1/ len(scores) for x in scores]
                    scores = utils.adjustScores(scores)
                    for i,x in enumerate(scores):
                        coin_info[coins[i]]['weight'] = x

                    
                

                # log coin allocations and portfolio value
                portfolio_value.append((time, cash + sum([((coin_info[x]['cash_invested'] / coin_info[x]['enter_value']) * coin_info[x]['last_close_price']) for x in coin_info if coin_info[x]['in_position']])))
                for coin in coins:
                    weights[coin].append((time, coin_info[coin]['weight']))
                    if coin_info[coin]['in_position']:
                        coin_allocations[coin].append((time, ((coin_info[coin]['cash_invested'] / coin_info[coin]['enter_value']) * coin_info[coin]['last_close_price']) / portfolio_value[-1][1]))
                    else:
                        coin_allocations[coin].append((time, 0.0))
                coin_allocations['CASH'].append((time, cash / portfolio_value[-1][1]))

                bar()

        for coin in coins:
            if coin_info[coin]['in_position']:
                coin_info[coin]['in_position'] = False
                exits[coin].append((time, coin_info[coin]['last_close_price']))
                new_cash_value = (1-self.fees)*((coin_info[coin]['cash_invested'] / coin_info[coin]['enter_value']) * coin_info[coin]['last_close_price'])
                profit = (new_cash_value / ((coin_info[coin]['cash_invested'] * (1 + self.fees)))) - 1
                coin_info[coin]['recent_trade_results'].append((profit, (coin_info[coin]['last_start_time'], coin_info[coin]['last_close_price'])))
                coin_info[coin]['cash_invested'] = 0.0
                cash += new_cash_value

        
        
        print(f'Cash: {cash}')
        writePMReport(coin_datasets, entries, exits, portfolio_value, coin_allocations, weights, self.indicators_to_graph, self.fees)

    '''         
    ARGS:
        -> None
    RETURN:
        -> None
    WHAT: 
        -> backtests each strategy on each dataset pair
        -> handles genetic algorithm if we are attempting to optimize parameters
    '''
    def backtest(self, processes=-1):
        coin_names = [x[1] for x in self.df_groups]
        print('Importing Strategies...')
        score, trades = 0, 0
        strategy_objs = []
        # dynamically load strategy objects and call their constructors
        for x in self.strategies:
            entry_models_info, exit_models_info = [], []
            for m in x['entry_models']:
                entry_models_info.append([m['name'], m['version']])
            for m in x['exit_models']:
                exit_models_info.append([m['name'], m['version']])
            strategy_objs.append(self.importStrategy(x)(coin_names=coin_names, entry_models=entry_models_info, exit_models=exit_models_info))

        self.strategies = strategy_objs
        # run genetic algorithm if specified by config
        if self.test_param_ranges:
            self.geneticExecution()

        # execute each strategy
        for x in self.strategies:
            coin_datasets = []
            first_times = set()
            i = 0
            # execute the strategy on each dataset group
            for dataset_chunks, dataset_name in self.df_groups:
                # generate data for each dataset in the group
                print(f'Working on coin {dataset_name}...')
                print('Generating Model Data...')
                new_features = self.generateIndicatorData(dataset_chunks, x.indicators)

                
                # we'll store the starting time of each dataset chunk here, to ensure we don't trade in between chunks
                

                # construct a single dataframe from all of the individual dataframes in the group, and construct the first_times set
                dataset = pd.DataFrame()
                dataset = pd.concat(dataset_chunks)
                
                

                if self.scale:
                    print('Scaling Model Data...')
                    utils.realtimeScale(dataset, new_features, 15000)
                    
                print('Preprocessing Model Predictions...')

                x.preProcessing(dataset, dataset_name)
                
                print('Generating Algo Data...')
                dataset = pd.DataFrame()
                new_features = self.generateIndicatorData(dataset_chunks, x.algo_indicators)
                
                for d in dataset_chunks:
                    
                    # DONT CHANGE THIS PLS THX
                    first_times.add(d.head(1).time.values[0])
                dataset = pd.concat(dataset_chunks)
                dataset.dropna(inplace=True)
                dataset.reset_index(inplace=True, drop=True)
                dataset = dataset[new_features + ['close', 'time', 'open', 'high', 'low']]
                
                self.df_groups[i][0] = []
                coin_datasets.append((dataset_name, dataset))
                i += 1

            print('Executing Strategy...')
            if len(coin_datasets) == 1:      
                
                # execute the strategy on the dataset       
                score, entries, exits = self.executeStrategy(x, coin_datasets[0][1], first_times, coin_datasets[0][0], plot=self.plot)
                trades = len(entries)
            else:
                self.executePM(coin_datasets=coin_datasets, start_times=first_times, strategy=x)
        return score, trades

    def generateIndicatorData(self, dataset_chunks, indicator_objects, gen_new_values=False):
        got_new_features = False
        new_features =  []
        for chunk in dataset_chunks:
            
            for ind in indicator_objects:
                new_fs = ind.genData(chunk, False)
                if not got_new_features:
                    new_features.extend(new_fs)
            got_new_features = True

            chunk.dropna(inplace=True)
            chunk.reset_index(inplace=True, drop=True)
        return new_features

    '''
    ARGS:
        -> None
    RETURN:
        -> None
    WHAT: 
        -> uses genetic algorithm to backtest each strategy on each dataset pair
        -> uses genetic config to load options for genetic algorithm (genetic.hjson)
    '''
    def geneticExecution(self):
        #load genetic configurations specified in genetic.hjson
        genetic_config = load_config("genetic.hjson")

        max_generations = genetic_config["max_generations"]
        population_size = genetic_config["organisms"]

        score_memoize = {}

        for x in self.strategies:
            for d in self.dfs:
                #make sure all of the data percentages adds to %100 of the data
                if np.round(genetic_config["train_data"] + genetic_config["test_data"] + genetic_config["validation_data"], 2) != 1.0:
                    raise ValueError("The percentages do not add to one for genetic algorithm, please edit genetic.hjson")
                
                # store the original dataset
                original_dataset = d

                #splitting up the data into train/test/val
                train_number = int(genetic_config["train_data"] * len(original_dataset))
                test_number = int(genetic_config["test_data"] * len(original_dataset))
                
                #df.loc[1:3, :]
                train_data = original_dataset.loc[:train_number, :]
                test_data = original_dataset.loc[train_number:train_number+test_number, :]
                val_data = original_dataset.loc[train_number + test_number:, :]

                test_pop_number = genetic_config["test_n_population"]

                # grab the indicators for the given strategy
                indicators = x.indicators

                # flag to keep track of whether or not genetic algorithm has reached threshold 
                # necessary to end execution
                done = False

                # keep track of best score so far
                prev_best_score = 0.0

                # run until improvement is small enough to exit
                gen_count = 1
                padding_count = 0
                while not done and gen_count <= max_generations:
                    new_best_score = prev_best_score
                    test_best_score = 0
                    # update the param ranges
                    if gen_count != 1:
                        for ind in indicators:
                            ind.shrinkParamRanges(genetic_config["shrink_algo"], genetic_config["param_range_percentage"])
                    
                    # each element of the population is a set of parameters the strategy is executed with
                    for p in tqdm(range(1, population_size+1)):

                        # generate data for the new set of parameters (which have effect on indicators)
                        dataset = pd.DataFrame
                        #check to see if this is a generation where we want to run the train or test set
                        if gen_count % test_pop_number != 0 and gen_count != max_generations:
                            dataset = train_data
                        else:
                            dataset = test_data

                        for ind in indicators:
                            ind.genData(dataset)
                        
                        # retrain the model if the strategy has the model-training built-in
                        if x.is_ml:
                            x.train(dataset)

                        #check if in memo table so don't have to run it again
                        data_id = "train" if gen_count % test_pop_number != 0 and gen_count != max_generations else "test"
                        possible_key = data_id
                        
                        for ind in indicators:
                            for p in ind.params:
                                possible_key += (p.name + str(p.value))
                        
                        # possible_key = str(indicators + data_id)

                        score = 0
                        if possible_key in score_memoize:
                            print("hit memo")
                            score = score_memoize[possible_key]
                        else:
                            # execute the strategy and grab the exit value
                            score = self.executeStrategy(x, (dataset, d[1]), plot=False, should_print=False)[0]
                            score_memoize[possible_key] = score

                        # store the param values if this is a new high score
                        if gen_count % test_pop_number != 0 and gen_count != max_generations:
                            if score > new_best_score:
                                new_best_score = score
                                padding_count = 0
                                for ind in indicators:
                                    ind.storeBestValues()
                        else:
                            if score > test_best_score:
                                test_best_score = score
                                for ind in indicators:
                                    ind.storeBestValues()
                    # if the best scorer for this population is less than 0.5% better than the previous best score,
                    # this will be the last generation
                    if new_best_score < (1 + genetic_config["exit_score"]) * prev_best_score and gen_count % test_pop_number != 0:
                        if padding_count >= genetic_config["padding_num"]:
                            done = True
                        padding_count += 1
                    else:
                        # if not, continue to the next generation and note this generation's best score
                        if gen_count % test_pop_number != 0 and gen_count != max_generations:
                            prev_best_score = new_best_score
                        else:
                            prev_best_score = test_best_score
                    print("Best score of the {} generation is: {}".format(gen_count, prev_best_score))
                    best_values = []
                    for ind in indicators:
                        best_values.append(ind.best_values)
                    print(best_values)
                    gen_count += 1
                
                # grab the best param values for each indicator
                best_values = []
                for ind in indicators:
                    best_values.append(ind.best_values)

                # write the best param values and best overall score to the console
                print(best_values)
                print(prev_best_score)

                dataset = val_data
                for ind in indicators:
                    ind.genData(dataset)
                if x.is_ml:
                    x.train(dataset)

                # execute the strategy and grab the exit value
                print("\n\nScore when tested on validation set: {}\n\n".format(self.executeStrategy(x, (dataset, d[1]))[0]))


    def segmented_genetic_execution(self):
        #load genetic configurations specified in genetic.hjson
        genetic_config = load_config("genetic.hjson")

        max_generations = genetic_config["max_generations"]
        population_size = genetic_config["organisms"]

        for x in self.strategies:
            for d in self.dfs:
                
                # grab the indicators for the given strategy
                indicators = x.indicators

                # flag to keep track of whether or not genetic algorithm has reached threshold 
                # necessary to end execution
                done = False

                # keep track of best score so far
                prev_best_score = 0.0

                dataset = d
                # run until improvement is small enough to exit
                gen_count = 1
                while not done and gen_count <= max_generations:
                    new_best_score = prev_best_score
                    test_best_score = 0
                    # update the param ranges
                    for ind in indicators:
                        ind.shrinkParamRanges(genetic_config["shrink_algo"], genetic_config["param_range_percentage"])
                    
                    # each element of the population is a set of parameters the strategy is executed with
                    for p in range(1, population_size+1):

                        for ind in indicators:
                            ind.genData(dataset)

                        n = len(dataset.index) // 5
                        df_chunks = [dataset[i:i+n] for i in range(0,dataset.shape[0],n)]
                        chunk_scores = []
                        for i, chunk in enumerate(df_chunks[:-1]):
                            total_profit, entries, exits = self.executeStrategy(x, (chunk, 'chunk' + str(i)), genetic_config["print_all"])[0]
                            num_profitable = 0
                            for p in range(min(len(entries), len(exits))):
                                if exits[p] > entries[p] + (exits[p] + entries[p] * self.fees):
                                    num_profitable += 1
                            chunk_scores.append(num_profitable / len(exits))
                        score = np.mean(chunk_scores)
                        # store the param values if this is a new high score
                        if gen_count != max_generations:
                            if score > new_best_score:
                                new_best_score = score
                                padding_count = 0
                                for ind in indicators:
                                    ind.storeBestValues()
                        else:
                            if score > test_best_score:
                                test_best_score = score
                                for ind in indicators:
                                    ind.storeBestValues()
                    # if the best scorer for this population is less than 0.5% better than the previous best score,
                    # this will be the last generation
                    if new_best_score < (1 + genetic_config["exit_score"]) * prev_best_score:
                        if padding_count >= genetic_config["padding_num"]:
                            done = True
                        padding_count += 1
                    else:
                        # if not, continue to the next generation and note this generation's best score
                        if gen_count != max_generations:
                            prev_best_score = new_best_score
                        else:
                            prev_best_score = test_best_score
                    print("Best score of generation {} is: {}".format(gen_count, prev_best_score))
                    gen_count += 1
                
                # grab the best param values for each indicator
                best_values = []
                for ind in indicators:
                    best_values.append(ind.best_values)

                # write the best param values and best overall score to the console
                print(best_values)
                print(prev_best_score)