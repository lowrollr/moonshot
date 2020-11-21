


import numpy as np

from sys import maxsize
from sklearn.preprocessing import QuantileTransformer

from v2.utils import findParams
from v2.strategy.indicators.indicator import Indicator




class Optimal_v2(Indicator):


    def genData(self, dataset, gen_new_values=True, value='close'):

        movements = []
        joined_movements = []

        
        cur_min = maxsize
        cur_max = 0.00
        cur_min_time = 00.0
        cur_max_time = 00.0
        
        
        looking_for_buy = True
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
                    
            else:
                if close > cur_max:
                    cur_max = close
                    cur_max_time = time
                else:
                    looking_for_buy = True
                    movements.append(((cur_min_time, cur_max_time), (cur_min, cur_max)))
                    cur_min = close
                    cur_min_time = time
                    cur_max = close
                    cur_max_time = time
                    
        cur_movement = [movements[0]]
        if len(movements) > 1:
            for (start, end), (buy, sell) in movements[1:]:
                if sell > cur_movement[-1][1][0]:
                    cur_movement.append(((start, end), (buy, sell)))
                else:
                    joined_movements.append(cur_movement)
                    cur_movement.append(((start, end), (buy, sell)))

        joined_movements.append(cur_movement)
        entry_weights = {}
        exit_weights = {}

        for x in joined_movements:
            overall_entry = x[0][1][0]
            overall_exit = x[-1][1][1]
            for (start, end), (buy, sell) in x:
                profit_perc = (sell - buy) / buy
                delta_entry = buy - overall_entry
                delta_exit = overall_exit - sell
                weight_entry = (1 / (0.001 + delta_entry)) * profit_perc
                weight_exit = (1 / (0.001 + delta_exit)) * profit_perc
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
        
        dataset['optimal'] = dataset.apply(lambda x: fillDatasetHelper(x.time), axis=1)
