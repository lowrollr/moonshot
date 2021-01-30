
from collections import deque

import time

import dash
import dash_core_components as dash_doc
import dash_html_components as dash_html


class DataStream:
    def __init__(self, name):
        self.name = name
        self.day_data = deque(maxlen=1440)
        self.week_data = deque(maxlen=1440)
        self.month_data = deque(maxlen=1440)
        self.year_data = deque(maxlen=2190)
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
        
        if now >= self.last_updated_month + 13020:
            self.week_data.append(value)
            self.last_updated_month = now
        else:
            self.week_data[-1] = value
        
        if now >= self.last_updated_year + 4752300:
            self.year_data.append(value)
            self.last_updated_year = now
        else:
            self.year_data[-1] = value
        