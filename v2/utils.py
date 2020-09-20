import time
import datetime

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