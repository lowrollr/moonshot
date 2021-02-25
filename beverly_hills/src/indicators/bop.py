from indicators.indicator import Indicator
from talib import BOP as talib_BOP
from data.data_queue import DataQueue
import numpy as np


class BOP(Indicator):
    def __init__(self, params, name, scalingWindowSize, unstablePeriod, value):
        super().__init__(params, name, scalingWindowSize, unstablePeriod, value)
        
        self.results = DataQueue(maxlen=self.windowSize)
    
    def compute(self, data):
        result = talib_BOP(np.asarray([data['open']], dtype=np.float64), np.asarray([data['high']], dtype=np.float64), np.asarray([data['low']], dtype=np.float64), np.asarray([data['close']], dtype=np.float64))[-1]
        self.results.addData(result)
        scaled_result = 0.5
        if self.results.curMax != self.results.curMin:
            scaled_result = (result - self.results.curMin) / (self.results.curMax - self.results.curMin)
        return {self.name: scaled_result}
        