
from collections import deque
import time

class Status:
    def __init__(self):
        self.last_ping = time.time()
        
    def ping(self):
        self.last_ping = time.time()

    def isOk(self):
        return int(self.last_ping + 5) >= int(time.time())

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
        self.p_value = 1.0
        self.positions = dict()
        for c in coins:
            self.positions[c] = dict()
    
    def openPosition(self, coin, amnt, price):
            self.positions[coin]['original_amnt'] = amnt
            self.positions[coin]['amnt'] = amnt
            self.positions[coin]['original_price'] = price
            self.positions[coin]['price'] = price
            self.positions[coin]['original_alloc'] = amnt*price / self.p_value
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

    def updatePosition(self, coin, coin_price):
        
        if self.positions[coin]:
            self.positions[coin]['price'] = coin_price
            self.positions[coin]['alloc'] = (self.positions[coin]['amnt']*coin_price) / self.p_value
            self.positions[coin]['profit'] = (coin_price / self.positions[coin]['original_price'] - 1) * 100


class DataStream:
    def __init__(self, name):
        self.name = name
        self.day_data = deque(maxlen=1440)
        self.day_data.append(1.0)
        self.week_data = deque(maxlen=1440)
        self.week_data.append(1.0)
        self.month_data = deque(maxlen=1440)
        self.month_data.append(1.0)
        self.year_data = deque(maxlen=1440)
        self.year_data.append(1.0)
        now = int(time.time())
        self.last_updated_day = now
        self.last_updated_week = now
        self.last_updated_month = now
        self.last_updated_year = now


    def update(self, value):
        now = int(time.time())
        while now >= self.last_updated_day + 60:
            self.day_data.append(self.day_data[-1])
            self.last_updated_day += 60
        self.day_data[-1] = value
        
        while now >= self.last_updated_week + 420:
            self.week_data.append(self.week_data[-1])
            self.last_updated_week += 420
        self.week_data[-1] = value

        while now >= self.last_updated_month + 1860:
            self.month_data.append(self.month_data[-1])
            self.last_updated_month += 1860
        self.month_data[-1] = value
        
        while now >= self.last_updated_year + 21900:
            self.year_data.append(self.year_data[-1])
            self.last_updated_year += 21900
        self.year_data[-1] = value
        
class PlotPositions:
    def __init__(self, coins):
        self.positions_to_plot_day = dict()
        self.positions_to_plot_week = dict()
        self.positions_to_plot_month = dict()
        self.positions_to_plot_year = dict()
        for coin in coins:
            self.positions_to_plot[coin] = deque([])

    def addNewPosition(self, coin, value, positionType):
        now = int(time.time())
        new_position = {'time': now, 'value': value, 'type': positionType}
        self.positions_to_plot_day[coin].append(new_position)
        self.positions_to_plot_week[coin].append(new_position)
        self.positions_to_plot_month[coin].append(new_position)
        self.positions_to_plot_year[coin].append(new_position)
        self.removeOldPositions()

    def removeOldPositions(self, now):

        while True:
            if self.positions_to_plot_day:
                position = self.positions_to_plot_day[0]
                if position['time'] + (1440 * 60) <= now:
                    self.positions_to_plot_day.popleft()
                else:
                    break
            else:
                break
                
        while True:
            if self.positions_to_plot_week:
                position = self.positions_to_plot_week[0]
                if position['time'] + (1440 * 60 * 7) <= now:
                    self.positions_to_plot_week.popleft()
                else:
                    break
            else:
                break

        while True:
            if self.positions_to_plot_month:
                position = self.positions_to_plot_month[0]
                if position['time'] + (1440 * 60 * 30) <= now:
                    self.positions_to_plot_month.popleft()
                else:
                    break
            else:
                break
        
        while True:
            if self.positions_to_plot_year:
                position = self.positions_to_plot_year[0]
                if position['time'] + (1440 * 60 * 365) <= now:
                    self.positions_to_plot_year.popleft()
                else:
                    break
            else:
                break

    