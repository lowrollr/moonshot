
from collections import deque
import time
from datetime import datetime

class Status:
    def __init__(self):
        self.last_ping = time.time()
        
    def ping(self):
        self.last_ping = time.time()

    def isOk(self):
        return int(self.last_ping + 5) >= int(time.time())

class Position:
    def __init__(self, coin, enter_time, enter_price, exit_price, amnt, alloc, now):
        self.coin = coin
        self.enter_time = enter_time
        self.exit_time = now
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
        self.p_value = 1.0
        self.positions = dict()
        for c in coins:
            self.positions[c] = dict()
    
    def openPosition(self, coin, amnt, price, now):
            self.positions[coin]['original_amnt'] = amnt
            self.positions[coin]['amnt'] = amnt
            self.positions[coin]['original_price'] = price
            self.positions[coin]['price'] = price
            self.positions[coin]['original_alloc'] = amnt*price / self.p_value
            self.positions[coin]['profit'] = 0.0
            self.positions[coin]['alloc'] = self.positions[coin]['original_alloc']
            self.positions[coin]['enter_time'] = now

    def closePosition(self, coin, amnt, price, now):
    
        if amnt == self.positions[coin]['amnt']:
            new_position_stream_position = Position(
                coin=coin,
                enter_time = self.positions[coin]['enter_time'],
                enter_price = self.positions[coin]['original_price'],
                exit_price = price,
                amnt = self.positions[coin]['original_amnt'],
                alloc = self.positions[coin]['original_alloc'],
                now= now
            )
            
            self.positions[coin] = dict()
            return new_position_stream_position
        else:
            self.positions[coin]['amnt'] -= amnt
            return None

    def updatePosition(self, coin, coin_price):
        
        if self.positions[coin]:
            self.positions[coin]['price'] = coin_price
            self.positions[coin]['alloc'] = (self.positions[coin]['amnt']*coin_price) / self.p_value
            self.positions[coin]['profit'] = (coin_price / self.positions[coin]['original_price'] - 1) * 100


class DataStream:
    def __init__(self, name):
        now_str = datetime.fromtimestamp(0).strftime('%Y-%m-%d %H:%M:%S')
        self.name = name
        self.initialized = False
        self.day_data = deque(maxlen=1440)
        self.day_data.append((1.0, 1, now_str))
        self.week_data = deque(maxlen=1440)
        self.week_data.append((1.0, 1, now_str))
        self.month_data = deque(maxlen=1440)
        self.month_data.append((1.0, 1, now_str))
        self.year_data = deque(maxlen=1440)
        self.year_data.append((1.0, 1, now_str))
        
        self.last_updated_day = 0
        self.last_updated_week = 0
        self.last_updated_month = 0
        self.last_updated_year = 0

    def initialize(self, data, now):
        now_str = datetime.fromtimestamp(now*60).strftime('%Y-%m-%d %H:%M:%S')
        self.day_data = deque(maxlen=1440)
        self.day_data.append((data, now, now_str))
        self.week_data = deque(maxlen=1440)
        self.week_data.append((data, now, now_str))
        self.month_data = deque(maxlen=1440)
        self.month_data.append((data, now, now_str))
        self.year_data = deque(maxlen=1440)
        self.year_data.append((data, now, now_str))
        self.last_updated_day = now
        self.last_updated_week = now
        self.last_updated_month = now
        self.last_updated_year = now
        self.initialized = True

    def update(self, value, now):
        now_str = datetime.fromtimestamp(now*60).strftime('%Y-%m-%d %H:%M:%S')
        while now > self.last_updated_day:
            self.day_data.append(self.day_data[-1])
            self.last_updated_day += 1
        self.day_data[-1] = (value, now, now_str)
        
        while now > self.last_updated_week + 7:
            self.week_data.append(self.week_data[-1])
            self.last_updated_week += 7
        self.week_data[-1] = (value, now, now_str)

        while now > self.last_updated_month + 31:
            self.month_data.append(self.month_data[-1])
            self.last_updated_month += 31
        self.month_data[-1] =(value, now, now_str)
        
        while now > self.last_updated_year + 365:
            self.year_data.append(self.year_data[-1])
            self.last_updated_year += 365
        self.year_data[-1] = (value, now, now_str)
        
class PlotPositions:
    def __init__(self, coins):
        self.positions_to_plot_day = dict()
        self.positions_to_plot_week = dict()
        self.positions_to_plot_month = dict()
        self.positions_to_plot_year = dict()
        for coin in coins:
            self.positions_to_plot_day[coin] = deque([])
            self.positions_to_plot_week[coin] = deque([])
            self.positions_to_plot_month[coin] = deque([])
            self.positions_to_plot_year[coin] = deque([])


    def addNewPosition(self, coin, value, positionType, now):
        
        new_position = {'time': now, 'datetime':  datetime.fromtimestamp(now*60).strftime('%Y-%m-%d %H:%M:%S'), 'value': value, 'type': positionType}
        self.positions_to_plot_day[coin].append(new_position)
        self.positions_to_plot_week[coin].append(new_position)
        self.positions_to_plot_month[coin].append(new_position)
        self.positions_to_plot_year[coin].append(new_position)
        

    def removeOldPositions(self, now, coin):

        while True:
            if len(self.positions_to_plot_day[coin]) > 0:
                position = self.positions_to_plot_day[coin].popleft()
                if position['time'] + (1440) <= now:
                    continue
                else:
                    self.positions_to_plot_day[coin].appendleft(position)
                    break
            else:
                break
                
        while True:
            if len(self.positions_to_plot_week[coin]) > 0:
                position = self.positions_to_plot_week[coin].popleft()
                if position['time'] + (1440 * 7) <= now:
                    continue
                else:
                    self.positions_to_plot_week[coin].appendleft(position)
                    break
            else:
                break

        while True:
            if len(self.positions_to_plot_month[coin]) > 0:
                position = self.positions_to_plot_month[coin].popleft()
                if position['time'] + (1440 * 31) <= now:
                    continue
                else:
                    self.positions_to_plot_month[coin].appendleft(position)
                    break
            else:
                break
        
        
        while True:
            if len(self.positions_to_plot_year[coin]) > 0:
                position = self.positions_to_plot_year[coin].popleft()
                if position['time'] + (1440 * 365) <= now:
                    continue
                else:
                    self.positions_to_plot_year[coin].appendleft(position)
                    break
            else:
                break

    