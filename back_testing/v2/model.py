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
from tqdm import tqdm
from itertools import product
import random

from v2.strategy.strategies.strategy import Strategy
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
        -> config ({String: Object}): param-value pairs read in from 'config.config' file
    RETURN:
        -> None
    WHAT: 
        -> initializes and configures the Trading class using the values read in from the config file
    '''
    def __init__(self, config):
        
        # Ensure logging/plotting directories are set up correctly
        utils.check_make_log_plot_dir()

        # We need to read in the fields from our config file and turn them into actionable parameters
        # Parse each field as needed and construct the proper paremeters
        self.base_cs = []
        self.quote_cs = []
        self.base_cs = config['ex1']
        self.quote_cs = config['ex2']
        self.freq = config['freq'][0]
        self.fees = float(config['fees'][0])
        self.indicators_to_graph = config['indicators_to_graph']
        self.strategy_list = config['strategy']
        self.version_list = config['strategy_version']
        self.strategies = []
        self.timespan = []
        self.slippage = float(config["slippage"][0])

        if config['timespan'][0] == 'max': # test over entire dataset
            self.timespan = [0, 9999999999]
        elif config["timespan"][0] == "date": # test from date_a to date_b (mm/dd/yyyy)
            self.timespan = utils.convert_timespan(config["timespan"][1:])
        elif len(config['timespan']) == 1: # date_a already defined in unix time, no need to convert
            self.timespan = [int(config['timespan'][0]), 9999999999]
        else: 
            self.timespan = [int(x) for x in config['timespan']]
        self.test_param_ranges = False
        if config['test_param_ranges'][0] == 'true':
            self.test_param_ranges = True
        self.plot = False
        if config['plot'][0] == 'true':
            self.plot = True
        
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
        datasets = []

        for b in base_currencies:
            for q in quote_currencies:
                # construct the appropriate filename 
                name = b + q
                filename = name + '_' + str(freq) + '.csv'
                # grab the dataset from the csv file
                my_df = pd.read_csv('historical_data/' + filename)
                my_df.columns = ['time', 'open', 'high', 'low', 'close', 'volume', 'trades']
                # filter dataset to only include data from the configured timespan 
                my_df = my_df[(my_df.time > self.timespan[0]) & (my_df.time < self.timespan[1])]
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
    
        

    def executeStrategy(self, strategy, my_dataset, *args):
        # STRATEGY VARIABLES
        position_quote = 1000000.00
        start = position_quote
        position_base = 0.00
        position_taken = False
        #filter by timespan
        dataset = my_dataset[0]
        dataset_name = my_dataset[1]
        
        #filter by indicators
        inc_fees = 0.0
        close = 0.0
        log = []
        slippage_log = []
        old_quote = 0.0
        
        slippage_tot = 0.0
        slippage_pos_base = 0.00
        slippage_pos_quote = position_quote
        slippage_fees = 0.0

        #PLOT VARIABLES
        entries = []
        exits = []

        #haven't implemneted slippage plot yet
        if self.plot:
            candle = go.Candlestick(x=dataset['time'], open=dataset['open'], close=dataset['close'], high=dataset['high'], low=dataset['low'], name='Candlesticks')
            inds = []
            data = []
            
            for x in self.indicators_to_graph:
                if x in dataset.columns: 
                    rand_color = 'rgba(' + str(random.randint(0, 255)) + ', ' + str(random.randint(0, 255)) + ', ' + str(random.randint(0, 255)) + ', 50)'
                    inds.append(go.Scatter(x=dataset['time'], y=dataset[x], name=x, line=dict(color=(rand_color))))
        
        #simulate backtesting
        for row in tqdm(dataset.itertuples()):
            close = row.close
            slippage_close = close

            if strategy.is_ml:
                #need to train over the dataset
                strategy.process(row, my_dataset[0])
            else:
                strategy.process(row)
            if not position_taken:
                if strategy.calc_entry(row):
                    position_taken = True

                    inc_fees = position_quote * self.fees
                    old_quote = position_quote
                    position_base = position_quote / close
                    position_quote = 0.0
                    entries.append([row.time, close])
                    log.append(str(row.time) + ': bought at ' + str(row.close))
                    
                    if self.slippage != 0:
                        slippage_fees = slippage_pos_quote * self.fees
                        slippage_close = utils.add_slippage("pos", close, self.slippage)
                        slippage_log.append(str(row.time) + ': bought at ' + str(slippage_close) + " tried to buy at " + str(close))
                        slippage_pos_base = slippage_pos_quote / slippage_close
                        slippage_tot += close - slippage_close
                        slippage_pos_quote = 0.0

            else:
                if strategy.calc_exit(row):
                    position_taken = False
                    position_quote = position_base * close
                    position_quote = position_quote * (1 - self.fees)
                    position_quote -= inc_fees
                    delta = position_quote - old_quote
                    position_base = 0.0
                    exits.append([row.time, close])
                    log.append(str(row.time) + ': sold at ' + str(row.close) + ' porfolio value: ' + str(position_quote) + ' delta: ' + str(delta))

                    if self.slippage != 0:
                        slippage_close = utils.add_slippage("neg", close, self.slippage)
                        slippage_pos_quote = slippage_pos_base * slippage_close
                        slippage_pos_quote = slippage_pos_quote * (1 - self.fees)
                        slippage_pos_quote -= slippage_fees
                        slippage_tot += slippage_close - close
                        slippage_pos_base = 0.0
                        slippage_log.append(str(row.time) + ": sold at " + str(slippage_close) + " tried to sell at " + str(close))

        name = 'results-' + strategy.name + '-' + dataset_name
        if args:
            name += '-' + args[0]
        if self.plot:
            #plot graph
            if entries:
                ent_graph = go.Scatter(x=[item[0] for item in entries], y=[item[1] for item in entries], name='Entries', mode='markers')
                exit_graph = go.Scatter(x=[item[0] for item in exits], y=[item[1] for item in exits], name='Exits', mode='markers')
                data = [candle] + inds + [ent_graph, exit_graph]
            else:
                data = inds
            if hasattr(strategy, 'scatter_x'):
                data += [strategy.get_stop_loss_plot()]
            layout = go.Layout(title=name)
            fig = go.Figure(data=data, layout=layout)
            plot(fig, filename='plots/' + name + '.html')

        conv_position = position_quote
        #output final account value
        if position_base:
            conv_position = (position_base * close) * (1 - self.fees)

        slippage_conv_pos = slippage_pos_quote
        if self.slippage != 0:
            slippage_close = utils.add_slippage("neg", close, self.slippage)
            slippage_conv_pos = (slippage_pos_base * slippage_close) * (1 - self.fees)

        std_dev = utils.get_log_std(log)
        # TODO: fix below
        # str_time, avg_time = utils.get_log_avg_hold(log)
        
        print('Exit value: ' + str(conv_position))
        if self.slippage != 0:
            print("Exit value " + str(slippage_conv_pos) + " with slippage value of " + str(self.slippage))
        print('Delta: ' + str(conv_position - start) + ' ' + str(((conv_position / start) * 100) - 100) + '%')
        print("Total trades made: " + str(len(entries)))
        if len(entries):
            print("Average gain/loss per trade: " + str((conv_position - start) / len(entries)))
        print("Standard deviation of the deltas (how volatile) " + str(std_dev))
        # print("Average time each trade is held " + str(str_time) + "(" + str(avg_time) + ")")

        # log trades
        with open('logs/' + name + '.txt', 'w') as f:
            for line in log:
                f.write(line + '\n')

        with open('slippage_logs/' + name + '.txt', 'w') as f:
            for line in slippage_log:
                f.write(line + '\n')

        return conv_position


    def backtest(self):
        #dynamically load strategies
        for x in range(len(self.strategy_list)):
            self.strategies.append(self.importStrategy(self.strategy_list[x], self.version_list[x])())


        #execute each strategy on each dataset
        for x in self.strategies:
            for d in self.dfs:
                dataset = d[0]
                if self.test_param_ranges:
                    original_dataset = d[0]
                    indicators = x.indicators
                    pop_size = 80
                    best_values = []
                    done = False
                    prev_best_score = 0.0
                    while not done:
                        new_best_score = prev_best_score
                        # update the param ranges
                        for ind in indicators:
                            ind.shrinkParamRanges(0.375)
                        
                        for p in range(0, pop_size):
                            dataset = original_dataset
                            for ind in indicators:
                                ind.genData(dataset)
                            if x.is_ml:
                                x.train(dataset)
                            score = self.executeStrategy(x, (dataset, d[1]))
                            if score > new_best_score:
                                new_best_score = score
                                for ind in indicators:
                                    ind.storeBestValues()
                                
                        if new_best_score < 1.005 * prev_best_score:
                            done = True
                        else:
                            prev_best_score = new_best_score
                        #check if we should continue or not
                    best_values = []
                    for ind in indicators:
                        best_values.append(ind.best_values)
                    print(best_values)
                    print(prev_best_score)
                        


                else:
                    for ind in x.indicators:
                        ind.genData(d[0], False)      
                    self.executeStrategy(x, d)

