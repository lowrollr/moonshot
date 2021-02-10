
from collections import deque

import time

class Status:
    def __init__(self):
        self.last_ping = time.time()
        
    def ping(self):
        self.last_ping = time.time()

    def isOk(self):
        return self.last_ping + 5 >= time.time()

class Position:
    def __init__(self, coin, enter_time, enter_price, exit_price, amnt, alloc):
        self.coin = coin
        self.enter_time = enter_time
        self.exit_time = time.time()
        self.enter_price = enter_price
        self.exit_price = exit_price
        self.amnt = amnt
        self.alloc = alloc

class PositionStream:
    def __init__(self, coins):
        self.all_positions = deque(maxlen=200)
        self.coin_positions = dict()
        for c in coins:
            self.coin_positions[c] = deque(maxlen=20)

class Positions:
    def __init__(self, coins):
        self.positions = dict()
        for c in coins:
            self.positions[c] = dict()
    
    def openPosition(self, coin, amnt, price, alloc, p_value):
        self.positions[coin]['original_amnt'] = amnt
        self.positions[coin]['amnt'] = amnt
        self.positions[coin]['original_price'] = price
        self.positions[coin]['price'] = price
        self.positions[coin]['original_alloc'] = amnt*price / p_value
        self.positions[coin]['profit'] = 0.0
        self.positions[coin]['alloc'] = self.positions[coin]['original_alloc']
        self.positions[coin]['enter_time'] = time.time()

    def closePosition(self, coin, amnt, price):
        if amnt == self.positions[coin]['amnt']:
            new_position_stream_position = Position(
                coin=coin,
                enter_time = self.positions[coin]['enter_time'],
                enter_price = self.postions[coin]['orginal_price'],
                exit_price = price,
                amnt = self.positions[coin]['original_amnt'],
                alloc = self.positions[coin]['original_alloc']
            )
            
            self.positions[coin] = dict()
            return new_position_stream_position
        else:
            self.positions[coin]['amnt'] -= amnt
            return None

    def updatePositions(self, coin_prices, p_value):
        for p in self.positions:
            self.positions[p]['price'] = coin_prices[p]
            self.positions[p]['alloc'] = (self.positions[p]['amnt']*coin_prices[p]) / p_value
            self.positions[p]['profit'] = (coin_prices[p] / self.positions[p]['original_price'] - 1) * 100


class DataStream:
    def __init__(self, name):
        self.name = name
        self.day_data = deque(maxlen=1440)
        self.week_data = deque(maxlen=1440)
        self.month_data = deque(maxlen=1440)
        self.year_data = deque(maxlen=1440)
        self.last_updated_day = 0
        self.last_updated_week = 0
        self.last_updated_month = 0
        self.last_updated_year = 0


    def update(self, value):
        now = int(time.time())
        if now >= self.last_updated_day + 60:
            self.day_data.append(value)
            self.last_updated_day = now
        else:
            self.day_data[-1] = value

        if now >= self.last_updated_week + 420:
            self.week_data.append(value)
            self.last_updated_week = now
        else:
            self.week_data[-1] = value
        
        if now >= self.last_updated_month + 1860:
            self.week_data.append(value)
            self.last_updated_month = now
        else:
            self.week_data[-1] = value
        
        if now >= self.last_updated_year + 21900:
            self.year_data.append(value)
            self.last_updated_year = now
        else:
            self.year_data[-1] = value
        