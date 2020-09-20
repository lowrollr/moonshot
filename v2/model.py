import pandas as pd
import os
import importlib
import inspect
import random
import plotly.graph_objs as go
from plotly.offline import plot
from pyti.smoothed_moving_average import smoothed_moving_average as sma
from v2.strategy.strategy import Strategy
from tqdm import tqdm
from v2.strategy.strategy import Strategy
from itertools import product

class Trading:
    def __init__(self, config):
        self.base_cs = config['ex1']
        self.quote_cs = config['ex2']
        self.freq = config['freq'][0]
        self.fees = float(config['fees'][0])
        self.dfs = self.getPairDatasets(self.base_cs, self.quote_cs, self.freq)
        self.strategy_list = config['strategy']
        self.strategies = []
        self.timespan = []
        if config['timespan'][0] == 'max':
            self.timespan = [0, 9999999999]
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

    def getPairDatasets(self, _base_cs, _quote_cs, freq):
        datasets = []
        for b in _base_cs:
            for q in _quote_cs:
                name = b + q
                filename = name + '_' + str(freq) + '.csv'
                my_df = pd.read_csv('historical_data/' + filename)
                my_df.columns = ['time', 'open', 'high', 'low', 'close', 'volume', 'trades']
                datasets.append((my_df, name))
                
        return datasets
    
    def importStrategy(self, strategy):
        module = importlib.import_module('v2.strategy.{0}'.format(strategy))
        for mod in dir(module):
            obj = getattr(module, mod)
            if inspect.isclass(obj) and issubclass(obj, Strategy) and obj != Strategy:
                return obj
        return None
    
    def prepareDataset(self, dataset, indicators):
        try:
            for i in indicators:
                #3 letter code
                ind_type = i[0:3]
                #get params
                params = None
                if len(i) > 3:
                    params = i[4:].split('_')
                else:
                    params = [0]
                if ind_type == 'sma':
                    period = int(params[0])
                    dataset[i] = sma(dataset['close'].tolist(), period)
                #add more indicator options as we need

        except:
            print('dataset preparation error')



    def executeStrategy(self, strategy, my_dataset, *args):
        
        # STRATEGY VARIABLES
        position_quote = 1000000.00
        start = position_quote
        position_base = 0.00
        position_taken = False
        #filter by timespan
        dataset = my_dataset[0]
        dataset_name = my_dataset[1]
        time_filtered_dataset = dataset[(dataset.time > self.timespan[0]) & (dataset.time < self.timespan[1])]
        #filter by indicators
        filtered_dataset = time_filtered_dataset.filter(items=strategy.getIndicators() + ['time'])
        inc_fees = 0.0
        close = 0.0
        log = []
        old_quote = 0.0
        
        #PLOT VARIABLES
        entries = []
        exits = []
        if self.plot:
            candle = go.Candlestick(x=time_filtered_dataset['time'], open=time_filtered_dataset['open'], close=time_filtered_dataset['close'], high=time_filtered_dataset['high'], low=time_filtered_dataset['low'], name='Candlesticks')
            inds = []
            data = []
            for x in strategy.indicators:
                if x != 'close':
                    rand_color = 'rgba(' + str(random.randint(0, 255)) + ', ' + str(random.randint(0, 255)) + ', ' + str(random.randint(0, 255)) + ', 50)'
                    inds.append(go.Scatter(x=time_filtered_dataset['time'], y=time_filtered_dataset[x], name=x, line=dict(color=(rand_color))))
        
        #simulate backtesting
        for row in tqdm(filtered_dataset.itertuples()):
            close = row.close
            strategy.process(row)
            if not position_taken:
                if strategy.calc_entry(row):
                    position_taken = True
                    position_base = position_quote / close
                    inc_fees = position_quote * self.fees
                    old_quote = position_quote
                    position_quote = 0.0
                    entries.append([row.time, close])
                    log.append(str(row.time) + ': bought at ' + str(row.close))
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
        
        print('exit value: ' + str(conv_position))
        print('delta: ' + str(conv_position - start) + ' ' + str(((conv_position / start) * 100) - 100) + '%')
        print("total trades made: " + str(len(entries)))
        print("average gain/loss per trade: " + str((conv_position - start) / len(entries)))
        print("average time hold of loss")
        #this could give snese of vaolatility
        print("std dev of trades")

        # log trades
        with open('logs/' + name + '.txt', 'w') as f:
            for line in log:
                f.write(line + '\n')

        return conv_position


    def backtest(self):
        #dynamically load strategies
        for x in self.strategy_list:
            self.strategies.append(self.importStrategy(x)())

        #load list of indicators we'll need to insert into our dataframes
        all_needed_indicators = set()
        for x in self.strategies:
            new_indicators = x.getIndicators()
            all_needed_indicators.update(set(new_indicators))

        #prepare datasets
        for d in self.dfs:
            self.prepareDataset(d[0], all_needed_indicators)

        #execute each strategy on each dataset
        for x in self.strategies:
            for d in self.dfs:
                if x.is_ml:
                    x.train(d[0])
                if self.test_param_ranges:
                    params = x.get_param_ranges()
                    param_values = []
                    for p in params.keys():
                        low = params[p][0]
                        high = params[p][1]
                        step = params[p][2]
                        cur = low
                        vals = []
                        while cur < high:
                            vals.append((cur, p))
                            cur += step
                        if vals[-1] != high:
                            vals.append((high, p))
                        param_values += [vals]
                    param_product = list(product(*param_values))
                    max_return = 0.0
                    max_attrs = ''
                    for p in param_product:
                        for p2 in p:
                            setattr(x, p2[1], p2[0])
                        name = str(p2)
                        new_return = self.executeStrategy(x, d, name)
                        if new_return > max_return:
                            max_return = new_return
                            max_attrs = str(p2)
                    print('max params: ' + max_attrs)
                else:      
                    self.executeStrategy(x, d)

