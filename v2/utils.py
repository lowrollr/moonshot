import time
import datetime
import numpy as np
import random
import os

#should probs make a class but thats TODO
def date_to_unix(date_arr):
    dt = datetime.datetime(date_arr[0], date_arr[1], \
                    date_arr[2], date_arr[3], date_arr[4])
    unix = dt.timestamp()
    return int(unix)

def str_to_unix(date):
    year = 2020
    month = 1
    day = 1
    hour = 0
    min_ = 0
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
    date_arr = [year, month, day, hour, min_]
    return date_to_unix(date_arr)

def convert_timespan(full_arr):
    if len(full_arr) < 3 and len(full_arr) > 0:
        date1_str = full_arr[0].split(".")
        unix1 = str_to_unix(date1_str)
        unix2 = 9999999999
        if len(full_arr) == 2:
            date2_str = full_arr[1].split(".")
            unix2 = str_to_unix(date2_str)
        return [unix1, unix2]
    else:
        raise Exception("There is supposed to be one or two values for date")

def calc_combinations(params):
    total_distinct = 1
    for x in params:
        total_distinct = total_distinct * (params[x][1] - params[x][0]) / params[x][2]
    return total_distinct

def update_params(params, best_result):
    if best_result:
        for x in params:
            low = params[x][0]
            high = params[x][1]
            param_range = high - low
            center = best_result[x]
            new_low = min(low, center - (0.375 * param_range))
            new_high = max(high, center + (0.375 * param_range))
            params[x][0] = new_low
            params[x][1] = new_high
    
def mutate_population(params, pop_size):
    new_population = {}
    while(len(new_population.keys()) < pop_size):
        new_comb = {}
        for p in params:
            dec_digits = len(str(params[p][2]).split('.')[1])
            num_values = int((params[p][1] - params[p][0]) / params[p][2])
            new_comb[p] = round(params[p][0] + (random.randint(0, num_values) * params[p][2]), dec_digits)
        if str(new_comb) not in new_population:
            new_population[str(new_comb)] = new_comb
    return new_population
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

def check_make_log_plot_dir():
    dirs = ["logs", "slippage_logs", "plots"]
    for dir in dirs:
        if not os.path.isdir(str(dir)):
            os.system("mkdir " + str(dir))
