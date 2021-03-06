'''
FILE: utils.py
AUTHORS:
    -> Jacob Marshall (marshingjay@gmail.com)
    -> Ross Copeland (rhcopeland101@gmail.com)
WHAT:
    -> This file contains utility functions for backtesting
    -> Functions that don't have a home elsewhere can go here
'''

import time
import datetime
import numpy as np
import random
import os
import re
import sys
import multiprocessing as mp
from collections import deque
from itertools import repeat
import csv
from load_config import load_config

'''
ARGS:
    -> date_arr ([Int]): list of ints s.t. date_arr = [year, month, day, hour, minute]
RETURN:
    -> unix (Int): Time in unix time corresponding to the given date
WHAT: 
    -> Converts actual date in integer representation to unix date
'''
def dateToUnix(date_arr):
    dt = datetime.datetime(date_arr[0], date_arr[1], \
                    date_arr[2], date_arr[3], date_arr[4],\
                    tzinfo=datetime.timezone.utc)
    unix = dt.timestamp()
    return int(unix)


'''
ARGS:
    -> date ([String]): List of strings containing any of year, month, day, hour, minute
RETURN:
    -> (Int): Time in unix time corresponding to the given date
WHAT: 
    -> Converts actual date in string representation to unix date
'''
def strToUnix(date):
    # set date component defaults
    year = 2020
    month = 1
    day = 1
    hour = 0
    min_ = 0
    # add date components as they are available
    if len(date) >= 1:
        year = int(date[0])
    if len(date) >= 2:
        month = int(date[1])
    if len(date) >= 3:
        day = int(date[2])
    if len(date) >= 4:
        hour = int(date[3])
    if len(date) >= 5:
        min_ = int(date[4])
    # concatenate components together to form a list
    date_arr = [year, month, day, hour, min_]
    # convert list of ints to unix date and return
    return dateToUnix(date_arr)


'''
ARGS:
    -> full_arr ([String]): List of strings containing Date 1 & Date 2
RETURN:
    -> [unix1, unix2] ([Int]): Unix times for each datestring
WHAT: 
    -> Converts date string pair to unix time pair
    -> If only 1 date is provided, set unix2 to a large number
'''
def convertTimespan(full_arr):
    # if one or two dates are specified (required)
    if len(full_arr) < 3 and len(full_arr) > 0:
        # date components will be seperated with '.' characters
        date1_str = full_arr[0].split(".")
        # convert date 1 to unix time
        unix1 = strToUnix(date1_str)
        unix2 = 9999999999
        # convert date 2 to unix time if it exists
        if len(full_arr) == 2:
            date2_str = full_arr[1].split(".")
            unix2 = strToUnix(date2_str)
        # return the pair of unix times
        return [unix1, unix2]

    else: # throw error if number of dates is incorrect 
        raise Exception("config: Dates must be specified with one or two values")


def retreiveFees(fee_val, maker_taker):
    if type(fee_val) is str:
        fee_config = load_config("fee.hjson")
        if fee_val not in fee_config:
            raise Exception("The fee value is not defined within the fee config")
        else:
            return fee_config[fee_val][0][maker_taker], fee_config[fee_val], True
        pass
    else:
        return fee_val, [], False

'''
ARGS:
    -> logs ([String]): List of log strings (representing each line of the log file)
RETURN:
    -> (Float): 
WHAT: 
    -> Computes the Standard Deviation of all of the trades made
TODO:
    -> Test this to see if it works
'''    
def getLogStd(logs):
    nums = []
    for log in logs:
        log_arr = log.split(" ")
        if log_arr[1] == "sold":
            nums.append(float(log_arr[-1]))
    if len(nums) == 0:
        return 0
    return np.std(nums, dtype = np.float32)


'''
ARGS:
    -> logs ([String]): List of log strings (representing each line of the log file)
RETURN:
    -> time_mean (String, float): tuple of string representation and float of average hold of each position
WHAT: 
    -> Comutes the average hold time for each position
'''    
def getLogAvgHold(logs):
    times = []
    i = 0
    while i < len(logs):
        log_arr = logs[i].split(" ")
        if log_arr[1] == "bought":
            next_log_arr = logs[i+1].split(" ")
            buy_time = float(log_arr[0][:-1])
            sell_time = float(next_log_arr[0][:-1])
            times.append(sell_time - buy_time)
        i += 2
    if len(times) <= 0:
        return "0", 0
    time_mean = np.mean(times)
    return unixToTime(time_mean), time_mean


'''
ARGS:
    -> unix_val (Int): Unix time value
RETURN:
    -> period_str (String): Fancy string representation of unix time value 
WHAT: 
    -> Converts unix value to string representation that is easier to read
''' 
def unixToTime(unix_val):
    # make sure unix_val is int
    check_int = int(unix_val)
    # convert unix int to datetime object
    full_dt = datetime.datetime.fromtimestamp(check_int)
    # format string with datetime components
    period_str = str(full_dt.year - 1970) + " year(s) " + \
                str(full_dt.month) + " month(s) " + \
                str(full_dt.day) + " day(s) " + \
                str(full_dt.hour) + " hour(s) " + \
                str(full_dt.minute) + " minute(s) " + \
                str(full_dt.second) + " second(s) "
    return period_str


'''
ARGS:
    -> up_or_down (String):
    -> close_price (Float):
    -> slippage_val (Float):
RETURN:
    -> slip_val (Float): 
WHAT: 
    -> 
TODO:
    -> finish commenting this
    -> make error message sound more professional
''' 
def addSlippage(up_or_down, close_price, slippage_val):
    slip_val = 0
    if up_or_down == "pos":
        #mult by 100 for randrange only does int
        max_slip = int((close_price + close_price * slippage_val) * 100)
        int_close = int(close_price * 100)
        slip_val = random.randrange(int_close, max_slip) / 100
    elif up_or_down == "neg":
        #mult by 100 for randrange only does int
        min_slip = int((close_price - close_price * slippage_val) * 100)
        int_close = int(close_price * 100)
        slip_val = random.randrange(min_slip, int_close) / 100
    else:
        raise Exception("Hey you provided the wrong value (pos/neg)")
    return slip_val


'''
ARGS:
    -> None
RETURN:
    -> None
WHAT: 
    -> ensures that proper directories exist for:
        - logs
        - slippage logs
        - plots
    -> If they do not exist in the appropriate place, they are created
''' 
def checkLogPlotDir():
    # dirs to ensure the existence of
    dirs = ["logs", "slippage_logs", "plots"]
    for dir in dirs:
        if not os.path.isdir(str(dir)):
            # create the dir if necessary
            os.system("mkdir " + str(dir))


'''
ARGS:
    -> params ([Param]): list of param objects to look within
    -> params_to_find ([String]): list of param names to find within params
RETURN:
    -> results ([Param]): list of param objects matching with given param names
WHAT: 
    -> finds objects in master list of params that have one of the given names, returns the list of them
''' 
def findParams(params, params_to_find):
    results = []
    for x in params_to_find:
        results.append(next((y for y in params if y.name == x), None))
    return results

'''
ARGS:
    -> data_source (String): source directory to retrieve datasets from
RETURN:
    -> base_currencies ([String]): list of strings corresponding to coin datasets to retrive
WHAT:
    -> retrieves all currencies from a certain data source
'''
def retrieveAll(starting_time=0, data_source='binance', freq='1m'):
    base_currencies = []
    data_dir = f"./historical_data/{data_source}/"
    all_files = os.listdir(data_dir)
    for filename in all_files:
        if os.path.isdir(f'{data_dir}{filename}'):
            
            with open(f'{data_dir}{filename}/{freq}/{filename}USDT-{freq}-data_chunk000001.csv') as f:
                r=list(csv.reader(f))
                first_time = r[1][1]
                if int(first_time) <= starting_time:
                    base_currencies.append(filename)

    return base_currencies

'''
ARGS:
    -> values ([Float]): list of values from a dataframe column
    -> windowsize (Int): size of the window to scale over
RETURN:
    -> values ([Float]): scaled list of values for the dataframe column
WHAT: 
    -> scales (minmax) the values of a column over a given window size and returns the new column values
''' 
def realtimeScaleMP(values, windowsize):
    # get the min/max values over the time window for each row
    max_v = slidingWindow(values, windowsize, findmin=False)
    min_v = slidingWindow(values, windowsize, findmin=True)

    # scale the values
    for i,v in enumerate(values):
        # min == max will results in division by zero, so just set the value as 0.5
        if max_v[i] == min_v[i]:
            values[i] = 0.5
        else:
            values[i] = (values[i] - min_v[i]) / (max_v[i] - min_v[i])

    return values

'''
ARGS:
    -> dataset (Dataframe): dataset to scale 
    -> columns ([String]): names of the dataset columns that need to be scaled
    -> windowsize (Int): size of the window to scale over
RETURN:
    -> None
WHAT: 
    -> scales (minmax) the values of each column in the dataset
    -> uses multiprocessing to ensure this happens as fast as possible
''' 
def realtimeScale(dataset, columns, windowsize):
    
    process_pool = mp.Pool(mp.cpu_count())
    col_values = [dataset[c].values for c in columns]
    params = zip(col_values, repeat(windowsize))
    results = process_pool.starmap(realtimeScaleMP, params)
    for i, r in enumerate(results):
        dataset[columns[i]] = r
        

'''
ARGS:
    -> values ([Float]): values to find the minimum/maximum for over the given time window
    -> windowsize (Int): size of the window to scale over
    -> findmin (Bool): if true, find the minimum value for each row over the given time window
        -> if false, find the maximum value for each row over the given time window
RETURN:
    -> result ([Float]): list of minimum/maximum values for each row over the given time window
WHAT: 
    -> for each value, finds the minimum/maximum value from the previous n values, where n = windowsize
    -> stole this algorithm from leetcode LOL
''' 
def slidingWindow(values, windowsize, findmin=False):
    result = []
    q = deque()
    l = r = 0

    while r < len(values):
        if not findmin:
            while q and values[q[-1]] < values[r]:
                q.pop()
        else:
            while q and values[q[-1]] > values[r]:
                q.pop()
        q.append(r)

        
        if l > q[0]:
            q.popleft()
        
        result.append(values[q[0]])
        if r + 1 >= windowsize:
            l += 1
        r += 1
    
    return result


'''
ARGS:
    -> scores ([Float]): un-adjusted, normalized scores (sum up to 1)
    -> min_value (Float): minimum value that each score can take
    
RETURN:
    -> scores ([Float]): scores after adjustment
WHAT: 
    -> adjusts list of normalized scores such that they are all above a given minimum value while still adding up to 1
''' 
def adjustScores(scores, min_value=0.01, max_value = 0.5):
    amount_added = 0.0
    sum_non_min_scores = 0.0
    # lower bound scores by min_value and redistribute
    for i,x in enumerate(scores):
        if x <= min_value:
            amount_added += min_value - x
            scores[i] = min_value
        else:
            sum_non_min_scores += x
    for i,x in enumerate(scores):
        if x != min_value:
            proportion = x / sum_non_min_scores
            scores[i] -= amount_added * proportion
    amount_subtracted = 0.0
    sum_non_max_scores = 0.0
    # upper bound scores by max_value and redistribute
    for i,x in enumerate(scores):
        if x >= max_value:
            amount_subtracted += x - max_value
            scores[i] = max_value
        else:
            sum_non_max_scores += x
    for i,x in enumerate(scores):
        if x != max_value:
            proportion = x / sum_non_max_scores
            scores[i] += amount_subtracted * proportion
    return scores


'''
ARGS:
    -> scores ([Float]): un-adjusted, normalized scores (sum up to 1)
    -> min_value (Float): minimum value that each score can take
    
RETURN:
    -> scores ([Float]): scores after adjustment
WHAT: 
    -> adjusts list of normalized scores such that they are all above a given minimum value while still adding up to 1
''' 
def getRandomSpinner():
    return random.choice(['classic',
                          'stars',
                          'arrows',
                          'arrow',
                          'vertical',
                          'waves',
                          'waves2',
                          'waves3',
                          'horizontal',
                          'dots',
                          'dots_reverse',
                          'dots_waves',
                          'dots_waves2',
                          'ball_scrolling',
                          'balls_scrolling',
                          'ball_bouncing',
                          'balls_bouncing',
                          'dots_recur',
                          'bar_recur',
                          'pointer',
                          'arrows_recur',
                          'triangles',
                          'triangles2',
                          'brackets',
                          'balls_filling',
                          'notes',
                          'notes2',
                          'notes_scrolling',
                          'arrows_incoming',
                          'arrows_outgoing',
                          'real_arrow',
                          'fish',
                          'fish2',
                          'fish_bouncing',
                          'fishes',
                          'pulse'])

'''
ARGS:
    -> info ({String: value}): item from PM executor coin_info dictionary
    -> default_amnt (Float): allocation value to return if the trade queue is not ful
    -> low_amnt (Float): allocation value to return if the kelly value is negative
    
RETURN:
    -> kelly ([Float]): portion of portfolio to allocate
WHAT: 
    -> calculates the Kelly Criterion value for a specified asset given it's recent trade history
    -> https://www.investopedia.com/articles/trading/04/091504.asp

''' 
def calcKellyPercent(info, default_amnt=0.05, low_amnt=0.01, amnt_needed=20):
    trades = info['recent_trade_results']
    win_rate = info['win_rate']
    avg_win = info['avg_win']
    avg_loss = info['avg_loss']

    # if len(trades) >= amnt_needed:
        
    if avg_win and avg_loss:
        kelly = win_rate - ((1 - win_rate)/(avg_win/abs(avg_loss)))
        if kelly > 0:
            return kelly
        else:
            return low_amnt
        # elif avg_win:
        #     return 0.8
        # elif avg_loss:
        #     return low_amnt
        
    return default_amnt

'''



'''
def getCurrentReturn(info, fees):
    return ((((info['last_close_price'] * info['amnt_owned']) * (1-fees)) + info['intermediate_cash']) / info['position_cost']) - 1
    
def enterPosition(info, cash_allocated, fees, time):
    info['cash_invested'] = cash_allocated * (1 - fees)
    info['amnt_owned'] = info['cash_invested'] / info['last_close_price']
    info['position_cost'] = cash_allocated
    info['enter_value'] = info['last_close_price']
    info['in_position'] = True
    info['last_start_time'] = time

def exitPosition(info, fees, time):
    info['in_position'] = False
    new_cash = (1-fees) * (info['amnt_owned'] * info['last_close_price'])
    profit = ((new_cash + info['intermediate_cash']) / info['position_cost']) - 1
    info['recent_trade_results'].append((profit, (info['last_start_time'], time)))
    info['cash_invested'] = 0.0
    info['intermediate_cash'] = 0.0
    info['amnt_owned'] = 0.0
    return new_cash, profit