from indicators.indicator import Indicator
from talib import SAR as talib_PSAR
from data.data_queue import DataQueue
import numpy as np


class PSAR(Indicator):
    def __init__(self, params, name, scalingWindowSize, unstablePeriod, value):
        super().__init__(params, name, scalingWindowSize, unstablePeriod, value)
        self.acceleration = self.params['acceleration']
        self.maximum = self.params['maximum']
        self.results = DataQueue(maxlen=self.windowSize)
    
    def compute(self, data):
        result = talib_PSAR(np.asarray([data['high']], dtype=np.float64), np.asarray([data['close']], dtype=np.float64), acceleration=self.acceleration, maximum=self.maximum)[-1]
        self.results.addData(result)
        scaled_result = 0.5
        if self.results.curMax != self.results.curMin:
            scaled_result = (result - self.results.curMin) / (self.results.curMax - self.results.curMin)
        return {self.name: scaled_result}
        