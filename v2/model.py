import pandas as pd
import os
import importlib
import inspect
from pyti.smoothed_moving_average import smoothed_moving_average as sma




class Trading:
    def __init__(self, config):
        os.chdir(config['root'][0])
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

    def getPairDatasets(self, _base_cs, _quote_cs, freq):
        datasets = []
        for b in _base_cs:
            for q in _quote_cs:
                filename = b + q + '_' + str(freq) + '.csv'
                my_df = pd.read_csv('historical_data/' + filename)
                my_df.columns = ['time', 'open', 'high', 'low', 'close', 'volume', 'trades']
                datasets.append(my_df)
                
        return datasets
    
    def importStrategy(self, strategy):
        module = importlib.import_module('v2.strategy.{0}'.format(strategy))
        obj = getattr(module, dir(module)[-1])
        return obj
    
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



    def executeStrategy(self, strategy, dataset):
        
        position_quote = 1000000.00
        start = position_quote
        position_base = 0.00
        position_taken = False
        #filter by timespan
        filtered_dataset = dataset[(dataset.time > self.timespan[0]) & (dataset.time < self.timespan[1])]
        #filter by indicators
        filtered_dataset = filtered_dataset.filter(items=strategy.getIndicators())
        
        inc_fees = 0.0
        close = 0.0
        for row in filtered_dataset.itertuples():
            close = row.close
            strategy.process(row)
            if not position_taken:
                if strategy.calc_entry(row):
                    position_taken = True
                    position_base = position_quote / close
                    inc_fees = position_quote * self.fees
                    position_quote = 0.0
            else:
                if strategy.calc_exit(row):
                    position_taken = False
                    position_quote = position_base * close
                    position_quote = position_quote * (1 - self.fees)
                    position_quote -= inc_fees
                    position_base = 0.0
        if position_base:
            conv_position = (position_base * close) * (1 - self.fees)
            print('exit value (holding quote, inc final transaction fee): ' + str(conv_position))
            print('delta: ' + str(conv_position - start) + ' ' + str((conv_position / start) * 100) + '%')
        else:
            print('exit value (not holding quote): ' + str(position_quote))
            print('delta: ' + str(position_quote - start) + ' ' + str((position_quote / start) * 100) + '%')



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
            self.prepareDataset(d, all_needed_indicators)

        #execute each strategy on each dataset
        for x in self.strategies:
            for d in self.dfs:
                self.executeStrategy(x, d)



    