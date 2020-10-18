import pandas as pd
import os
import importlib
import inspect
import random
import plotly.graph_objs as go
from plotly.offline import plot

from v2.strategy.strategies.strategy import Strategy
from tqdm import tqdm
from itertools import product
import v2.utils as utils
import random

class Trading:
    def __init__(self, config):
        utils.check_make_log_plot_dir()
        self.base_cs = config['ex1']
        self.quote_cs = config['ex2']
        self.freq = config['freq'][0]
        self.fees = float(config['fees'][0])
        
        self.strategy_list = config['strategy']
        self.strategies = []
        self.timespan = []
        self.slippage = float(config["slippage"][0])
        if config['timespan'][0] == 'max':
            self.timespan = [0, 9999999999]
        elif config["timespan"][0] == "date":
            self.timespan = utils.convert_timespan(config["timespan"][1:])
        elif len(config['timespan']) == 1:
            self.timespan = [int(config['timespan'][0]), 9999999999]
        else:
            self.timespan = [int(x) for x in config['timespan']]
        self.test_param_ranges = False
        if config['test_param_ranges'][0] == 'true':
            self.test_param_ranges = True
        self.plot = False
        if config['plot'][0] == 'true':
            self.plot = True
        
        #this needs to happen last
        self.dfs = self.getPairDatasets(self.base_cs, self.quote_cs, self.freq)

    def getPairDatasets(self, _base_cs, _quote_cs, freq):
        datasets = []
        for b in _base_cs:
            for q in _quote_cs:
                name = b + q
                filename = name + '_' + str(freq) + '.csv'
                my_df = pd.read_csv('historical_data/' + filename)
                my_df.columns = ['time', 'open', 'high', 'low', 'close', 'volume', 'trades']
                my_df = my_df[(my_df.time > self.timespan[0]) & (my_df.time < self.timespan[1])]
                datasets.append((my_df, name))
                
        return datasets
    
    def importStrategy(self, strategy):
        module = importlib.import_module('v2.strategy.strategies.{0}'.format(strategy))
        for mod in dir(module):
            obj = getattr(module, mod)
            if inspect.isclass(obj) and issubclass(obj, Strategy) and obj != Strategy:
                return obj
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
            # for x in strategy.indicators:
            #     if x != 'close':
            #         rand_color = 'rgba(' + str(random.randint(0, 255)) + ', ' + str(random.randint(0, 255)) + ', ' + str(random.randint(0, 255)) + ', 50)'
            #         inds.append(go.Scatter(x=dataset['time'], y=dataset[x], name=x, line=dict(color=(rand_color))))
        
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
                data = [candle] + inds
            
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
        for x in self.strategy_list:
            self.strategies.append(self.importStrategy(x)())

        #load list of indicators we'll need to insert into our dataframes
        # all_needed_indicators = set()
        # for x in self.strategies:
        #     new_indicators = x.getIndicators()
        #     all_needed_indicators.update(set(new_indicators))

        # #prepare datasets
        # if not self.test_param_ranges:
        #     for d in self.dfs:
        #         self.prepareDataset(d[0], all_needed_indicators)

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
                        


                    # if necessary, prepare the dataset with each set of param values
                    # execute the strategy on the given dataset

                # if self.test_param_ranges:
                #     params = x.get_param_ranges()
                #     param_values = []
                #     for p in params.keys():
                #         low = params[p][0]
                #         high = params[p][1]
                #         step = params[p][2]
                #         cur = low
                #         vals = []
                #         while cur < high:
                #             vals.append((cur, p))
                #             cur += step
                #         if vals[-1] != high:
                #             vals.append((high, p))
                #         param_values += [vals]
                #     param_product = list(product(*param_values))
                #     max_return = 0.0
                #     max_attrs = ''
                #     for p in param_product:
                #         for p2 in p:
                #             setattr(x, p2[1], p2[0])
                #         name = str(p2)
                #         new_return = self.executeStrategy(x, d, name)
                #         if new_return > max_return:
                #             max_return = new_return
                #             max_attrs = str(p2)
                #     print('max params: ' + max_attrs)
                else:
                    for ind in x.indicators:
                        ind.genData(d[0], False)      
                    self.executeStrategy(x, d)

