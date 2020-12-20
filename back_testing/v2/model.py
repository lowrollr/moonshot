'''
FILE: model.py
AUTHORS:
    -> Jacob Marshall (marshingjay@gmail.com)
    -> Ross Copeland (rhcopeland101@gmail.com)
WHAT:
    -> This file contains the Trading class and its member functions,
    which implement all core functionaltiy of the backtesting framework
'''

import pandas as pd
import os
import importlib
import inspect
import random
import plotly.graph_objs as go
from plotly.offline import plot
import matplotlib.pyplot as plt
from tqdm import tqdm
from itertools import product
import random

from v2.strategy.strategies.strategy import Strategy
from v2.report import write_report
import v2.utils as utils

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
    def __init__(self, config):
        
        # Ensure logging/plotting directories are set up correctly
        utils.checkLogPlotDir()

        # We need to read in the fields from our config file and turn them into actionable parameters
        # Parse each field as needed and construct the proper paremeters
        self.base_cs = config['ex1']
        self.quote_cs = config['ex2']
        self.freq = config['freq']
        self.fees = float(config['fees'])
        self.indicators_to_graph = config['indicators_to_graph']
        self.strategy_list = config['strategy']
        self.version_list = config['strategy_version']
        self.strategies = []
        self.timespan = []
        self.slippage = float(config["slippage"])

        if config['timespan'] == 'max': # test over entire dataset
            self.timespan = [0, 9999999999]
        elif '.' in config["timespan"][0]:  # test from date_a to date_b military time (yyyy.mm.dd.hh.mm)
            self.timespan = utils.convertTimespan(config["timespan"])
        elif len(config['timespan']) == 1: # date_a already defined in unix time, no need to convert
            self.timespan = [int(config['timespan'][0]), 9999999999]
        else: 
            self.timespan = [int(x) for x in config['timespan']]
        
        
        self.test_param_ranges = config['test_param_ranges'] 
        
        
        self.plot = config['plot']
        
        # Load the appropriate datasets for each currency pair 
        # This happens last, depend on other config parameters
        self.dfs = self.getPairDatasets(self.base_cs, self.quote_cs, self.freq)


    '''
    ARGS:
        -> base_currencies ([String]): List of base currencies to fetch datasets for
        -> quote_currencies ([String]): List of quote currencies to fetch datasets for
        -> freq (Int): The timeframe to fetch datasets for (in minutes)
    RETURN:
        -> datasets ([Dataframe]): List of pandas dataframes, each containg a dataset
            for a base/quote pair
    WHAT: 
        -> fetches a dataset for each possible pair of <base currency>/<quote currency> 
            for the given timeframe
    '''
    def getPairDatasets(self, base_currencies, quote_currencies, freq):
        filenames = []
        datasets = []
        if base_currencies == ['all']:
            filenames = utils.retrieveAll(quote_currencies, freq)
        else:
            for b in base_currencies:
                for q in quote_currencies:
                    # construct the appropriate filename 
                    name = b + q
                    filename = name + '_' + str(freq) + '.csv'
                    filenames.append(filename)
                    # grab the dataset from the csv file
        for f in filenames:
            my_df = pd.read_csv('historical_data/' + f)
            my_df.columns = ['time', 'open', 'high', 'low', 'close', 'volume', 'trades']
            # filter dataset to only include data from the configured timespan 
            my_df = my_df[(my_df.time > self.timespan[0]) & (my_df.time < self.timespan[1])]
            name = f.split('_')[0]
            datasets.append((my_df, name))
                
        return datasets


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
    def importStrategy(self, strategy, version):
        # construct the base directory
        base_dir = 'v2.strategy.strategies.' + strategy

        if version == 'latest': # fetch the latest version of the given strategy
            all_files = os.listdir('./v2/strategy/strategies/' + strategy)
            highest_version = 0.0
            # find the highest version number
            for x in all_files:
                if x[0:len(strategy)] == strategy:
                    my_file = x.split('.py')[0]
                    my_version = my_file.split('_v')[1]
                    my_version = float(my_version.replace('_', '.'))
                    highest_version = max(my_version, highest_version)
                    
            # set version to be the highest version found
            version = str(highest_version).replace('.', '_')
        
        # this code attempts to find the module (strategy) with the given name, 
        # and gets the corresponding object if it exists
        module = importlib.import_module(base_dir + '.' + strategy + '_v' + version)
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
    WHAT: 
        -> Executes the given strategy on the dataset
        -> Calls the appropriate strategy procedures each tick
            i.e. calc_enrty() when looking to enter
                 calc_exit() when looking to exit
                 process() every tick
        -> This assumes that our entire position is converted from currency a to currency b and
            vice-versa when making a trade
        -> Optionally plots a candlestick chart showing entry/exit points
        -> Logs entry and exit points
        -> Calculates performance metrics and writes them to the console after executing
    TODO:
        -> This function does way too many things...
        -> Is slippage all the way implemented?
    '''
    def executeStrategy(self, strategy, my_dataset, *args):

        # initialize starting position to 1000000 units
        position_quote = 1000000.00
        start = position_quote
        # initialize base position to 0 units
        position_base = 0.00
        # this will keep track of whether or not we are engaged in a position in the base currency
        position_taken = False
        
        # the dataset itself will be the first part of the tuple passed
        dataset = my_dataset[0]
        # the name of the dataset is the second part
        dataset_name = my_dataset[1]
        
        # this keeps track of fees we incur by entering a postion in the base currency
        # these will be subtracted once we have converted our position back to the quote currency
        # (by closing our position or reaching the end of the dataset)
        inc_fees = 0.0

        # keeps track of the current close price (used within the loop as well as after)
        close = 0.0

        # store strings to write to the log here
        log = []

        # store string to write to the slippage log here
        slippage_log = []
        old_quote = 0.0
        
        # vars to keep track of slippage
        slippage_tot = 0.0
        slippage_pos_base = 0.00
        slippage_pos_quote = position_quote
        slippage_fees = 0.0

        # stores tuples (time, value) for when we enter/exit a position
        # these get plotted
        entries = []
        exits = []
        
        # this is the main loop for iterating through each row of the dataset
        for row in tqdm(dataset.itertuples()):
            # keep track of the close price for the given tick
            close = row.close
            slippage_close = close

            # run the process function (will execute anything that needs to happen each tick for the strategy)
            strategy.process(row)
            
            if not position_taken: # if we are not entered into a position

                # run the entry function for our strategy
                if strategy.calc_entry(row):
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
                    log.append(str(row.time) + ': bought at ' + str(row.close))
                    
                    

                    # do slippage things if we are keeping track of slippage
                    if self.slippage != 0:
                        slippage_fees = slippage_pos_quote * self.fees
                        slippage_close = utils.add_slippage("pos", close, self.slippage)
                        slippage_log.append(str(row.time) + ': bought at ' + str(slippage_close) + " tried to buy at " + str(close))
                        slippage_pos_base = slippage_pos_quote / slippage_close
                        slippage_tot += close - slippage_close
                        slippage_pos_quote = 0.0
                
                
            else: # otherwise, we are looking to exit a position
                
                # run the exit function of our strategy
                if strategy.calc_exit(row):
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
                    log.append(str(row.time) + ': sold at ' + str(row.close) + ' porfolio value: ' + str(position_quote) + ' delta: ' + str(delta))

                    # do slippage things if we are keeping track of slippage
                    if self.slippage != 0:
                        slippage_close = utils.add_slippage("neg", close, self.slippage)
                        slippage_pos_quote = slippage_pos_base * slippage_close
                        slippage_pos_quote = slippage_pos_quote * (1 - self.fees)
                        slippage_pos_quote -= slippage_fees
                        slippage_tot += slippage_close - close
                        slippage_pos_base = 0.0
                        slippage_log.append(str(row.time) + ": sold at " + str(slippage_close) + " tried to sell at " + str(close))
                

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
        slippage_conv_pos = slippage_pos_quote
        if self.slippage != 0:
            slippage_close = utils.add_slippage("neg", close, self.slippage)
            slippage_conv_pos = (slippage_pos_base * slippage_close) * (1 - self.fees)

        std_dev = utils.getLogStd(log)
        
        # write statistics to console
        print('Exit value: ' + str(conv_position))
        if self.slippage != 0:
            print("Exit value " + str(slippage_conv_pos) + " with slippage value of " + str(self.slippage))
        print('Delta: ' + str(conv_position - start) + ' ' + str(((conv_position / start) * 100) - 100) + '%')
        print("Total trades made: " + str(len(entries)))
        if len(entries):
            print("Average gain/loss per trade: " + str((conv_position - start) / len(entries)))
        print("Standard deviation of the deltas (how volatile) " + str(std_dev))
        
        # write to log
        with open('logs/' + name + '.txt', 'w') as f:
            for line in log:
                f.write(line + '\n')

        # write to slippage log
        with open('slippage_logs/' + name + '.txt', 'w') as f:
            for line in slippage_log:
                f.write(line + '\n')

        write_report(dataset, entries, exits, strategy.indicators, name)
        # return the final quote position
        return conv_position


    '''
    ARGS:
        -> None
    RETURN:
        -> None
    WHAT: 
        -> backtests each strategy on each dataset pair
        -> handles genetic algorithm if we are attempting to optimize parameters
    '''
    def backtest(self):
        # dynamically load strategy objects and call their constructors
        for x in range(len(self.strategy_list)):
            self.strategies.append(self.importStrategy(self.strategy_list[x], self.version_list[x])())

        # execute each strategy on each dataset
        for x in self.strategies:
            for d in self.dfs:

                dataset = d[0]

                if self.test_param_ranges: # if we are using the genetic algorithm to optimize parameters

                    # store the original dataset
                    original_dataset = d[0]

                    # grab the indicators for the given strategy
                    indicators = x.indicators

                    # set population size
                    pop_size = 80

                    # flag to keep track of whether or not genetic algorithm has reached threshold 
                    # necessary to end execution
                    done = False

                    # keep track of best score so far
                    prev_best_score = 0.0

                    # run until improvement is small enough to exit
                    while not done:
                        new_best_score = prev_best_score
                        # update the param ranges
                        for ind in indicators:
                            ind.shrinkParamRanges(0.375)
                        
                        # each element of the population is a set of parameters the strategy is executed with
                        for p in range(0, pop_size):

                            # generate data for the new set of parameters (which have effect on indicators)
                            dataset = original_dataset
                            for ind in indicators:
                                ind.genData(dataset)
                            
                            # retrain the model if the strategy has the model-training built-in
                            if x.is_ml:
                                x.train(dataset)

                            # execute the strategy and grab the exit value
                            score = self.executeStrategy(x, (dataset, d[1]))

                            # store the param values if this is a new high score
                            if score > new_best_score:
                                new_best_score = score
                                for ind in indicators:
                                    ind.storeBestValues()
                        # if the best scorer for this population is less than 0.5% better than the previous best score,
                        # this will be the last generation
                        if new_best_score < 1.005 * prev_best_score:
                            done = True
                        else:
                            # if not, continue to the next generation and note this generation's best score
                            prev_best_score = new_best_score
                    
                    # grab the best param values for each indicator
                    best_values = []
                    for ind in indicators:
                        best_values.append(ind.best_values)

                    # write the best param values and best overall score to the console
                    print(best_values)
                    print(prev_best_score)

                else: #if we are not running the genetic algorithm
                    # add all indicator data to the dataset
                    for ind in x.indicators:
                        ind.genData(d[0], False)
                    # execute the strategy on the dataset       
                    self.executeStrategy(x, d)

