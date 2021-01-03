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
    -> quote_currencies ([String]): list of quote currencies
    -> frequncy (String): string representation of frequency of the data
RETURN:
    -> list of strings of filenames to open
WHAT:
    -> checks to see which files meet the specification and that are not empty
'''
def retrieveAll(quote_currencies, frequency):
    base_currencies = []
    all_files = os.listdir("historical_data/")
    for filename in all_files:
        for q in quote_currencies:
            file_str = str(q) + "_" + str(frequency) + ".csv"
            if re.match(r'(\w+)'+ file_str, filename):
                match = re.match(r'(\w+)'+ file_str, filename)
                if os.stat("historical_data/" + match[0]).st_size == 0:
                    continue
                base_currencies.append(match[0])

    return base_currencies