'''
FILE: utils.py
AUTHORS:
    -> Jacob Marshall (marshingjay@gmail.com)
    -> Ross Copeland (rhcopeland101@gmail.com)
WHAT:
    -> This file contains utility functions for backtesting
    -> Functions that don't have a home elsewhere can go here
TODO:
    -> Should this be a class?
'''

import time
import datetime
import numpy as np
import random
import os

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
                    date_arr[2], date_arr[3], date_arr[4])
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

def convert_timespan(full_arr):
    if len(full_arr) < 3 and len(full_arr) > 0:
        date1_str = full_arr[0].split(".")
        unix1 = strToUnix(date1_str)
        unix2 = 9999999999
        if len(full_arr) == 2:
            date2_str = full_arr[1].split(".")
            unix2 = strToUnix(date2_str)
        return [unix1, unix2]
    else:
        raise Exception("Dates must be specified with one or two values")




    
def get_log_std(logs):
    nums = []
    for log in logs:
        log_arr = log.split(" ")
        if log_arr[1] == "sold":
            nums.append(float(log_arr[-1]))
    return np.std(nums, dtype = np.float32)

def get_log_avg_hold(logs):
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
    time_mean = np.mean(times)
    return unix_to_time(time_mean), time_mean

def unix_to_time(unix_val):
    check_int = int(unix_val)
    full_dt = datetime.datetime.fromtimestamp(check_int)
    period_str = str(full_dt.year - 1970) + " year(s) " + \
                str(full_dt.month) + " month(s) " + \
                str(full_dt.day) + " day(s) " + \
                str(full_dt.hour) + " hour(s) " + \
                str(full_dt.minute) + " minute(s) " + \
                str(full_dt.second) + " second(s) "
    return period_str

def add_slippage(up_or_down, close_price, slippage_val):
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

# Make sure the logging and plots directories exist in the appropriate places
# Add new directories if needed if they don't already exist
def check_make_log_plot_dir():
    dirs = ["logs", "slippage_logs", "plots"]
    for dir in dirs:
        if not os.path.isdir(str(dir)):
            os.system("mkdir " + str(dir))

def findParams(params, params_to_find):
    results = []
    for x in params_to_find:
        results.append(next((y for y in params if y.name == x), None))
    return results

