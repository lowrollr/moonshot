'''
FILE: optimal.py
AUTHORS:
    -> Jacob Marshall (marshingjay@gmail.com)
    -> Ross Copeland (rhcopeland101@gmail.com)
WHAT:
    -> This file contains the Optimal Indicator
'''
import numpy as np
from sys import maxsize
from sklearn.preprocessing import QuantileTransformer

from v2.utils import findParams
from v2.strategy.indicators.indicator import Indicator

'''
CLASS: Optimal
WHAT:
    -> Implements the Optimal Indicator
    -> Adds optimal buy/sell points to the dataset
    -> Params Required:
        -> None
'''
class Optimal(Indicator):

    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: weather or not we should generate new values for each param belonging
            to this Indicator
        -> value (String) <optional>: dataframe column name to use for calculations
    RETURN:
        -> None
    WHAT: 
        -> Adds columns with optimal buy/sell
    '''
    def genData(self, dataset, gen_new_values=True, value='close'):

        penalty = findParams(self.params, ['penalty'])[0]
        penalty_value = 0.0
        if penalty:
            if gen_new_values:
                penalty.genValue()
            penalty_value = penalty.value



        long_term_movements = {}
        entry_weights = {}
        exit_weights = {}



        cur_min = maxsize
        cur_max = 0.00
        cur_min_time = 00.0
        cur_max_time = 00.0
        last_buy_price = 000.00
        last_buy_time = 000.00
        sell_time = 0000.0
        looking_for_buy = True
        # Pass with Penalty
        for row in dataset.itertuples():
            close = row.close
            time = row.time
            if looking_for_buy:
                if close < cur_min:
                    cur_min = close
                    cur_min_time = time
                    cur_max = close
                    cur_max_time = time
                elif close > cur_max:
                    cur_max = close
                    cur_max_time = time
                    delta = cur_max - cur_min
                    if delta > ((cur_min * penalty_value) + (cur_max * penalty_value)):
                        looking_for_buy = False
                        last_buy_price = cur_min
                        last_buy_time = cur_min_time
            else:
                trade_penalty = ((cur_min * penalty_value) + (cur_max * penalty_value))
                if close > cur_max:
                    cur_max = close
                    cur_max_time = time
                elif close < cur_max - trade_penalty:
                    looking_for_buy = True
                    key_value = (cur_min_time, cur_max_time)
                    
                    long_term_movements[key_value] = {}
                    long_term_movements[key_value]['prices'] = (cur_min, cur_max)
                    long_term_movements[key_value]['submovements'] = []
                    cur_min = close
                    cur_min_time = time
                    cur_max = close
                    cur_max_time = time

        cur_min = maxsize
        cur_max = 0.00
        cur_min_time = 00.0
        cur_max_time = 00.0
        last_buy_price = 000.00
        last_buy_time = 000.00
        sell_time = 0000.0
        looking_for_buy = True
        # Pass without Penalty
        for row in dataset.itertuples():
            close = row.close
            time = row.time
            if looking_for_buy:
                if close < cur_min:
                    cur_min = close
                    cur_min_time = time
                    cur_max = close
                    cur_max_time = time
                elif close > cur_max:
                    cur_max = close
                    cur_max_time = time
                    
                    looking_for_buy = False
                    last_buy_price = cur_min
                    last_buy_time = cur_min_time
            else:
                if close > cur_max:
                    cur_max = close
                    cur_max_time = time
                else:
                    looking_for_buy = True
                    #iterate through long_term_movement keys
                    for start, end in long_term_movements.keys():
                        if time >= start and time <= end:
                            long_term_movements[(start, end)]['submovements'].append(\
                                ((cur_min_time, cur_max_time), (cur_min, cur_max)))
                    cur_min = close
                    cur_min_time = time
                    cur_max = close
                    cur_max_time = time


        for x in long_term_movements.keys():
            for (start, end), (entry_price, exit_price) in long_term_movements[x]['submovements']:
                profit_perc = (exit_price - entry_price) / entry_price
                delta_entry = entry_price - long_term_movements[x]['prices'][0]
                delta_exit = long_term_movements[x]['prices'][1] - exit_price
                weight_entry = (1 / (0.1 + delta_entry)) * profit_perc
                weight_exit = (1 / (0.1 + delta_exit)) * profit_perc
                entry_weights[start] = weight_entry
                exit_weights[end] = weight_exit
        
        entry_weights_list = list(entry_weights.values())
        exit_weights_list = list(exit_weights.values())


        q_scaler = QuantileTransformer()
        numpy_entry_weights = np.array(entry_weights_list).reshape(-1, 1)
        numpy_exit_weights = np.array(exit_weights_list).reshape(-1, 1)
        entry_weights_list = q_scaler.fit_transform(numpy_entry_weights)[:,0]
        exit_weights_list = q_scaler.fit_transform(numpy_exit_weights)[:,0]

        entry_weights_keys = list(entry_weights.keys())
        exit_weights_keys = list(exit_weights.keys())

        for k in range(len(entry_weights_keys)):
            entry_weights[entry_weights_keys[k]] = entry_weights_list[k]
        for k in range(len(exit_weights_keys)):
            exit_weights[exit_weights_keys[k]] = exit_weights_list[k]

        def fillDatasetHelper(time):
            if time in entry_weights:
                return entry_weights[time]
            elif time in exit_weights:
                return -1 * exit_weights[time]
            else:
                return 0.0
        
        dataset[self.name] = dataset.apply(lambda x: fillDatasetHelper(x.time), axis=1)
        return [self.name]



