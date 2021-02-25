from indicators.indicator import Indicator
from talib import WILLR as talib_WILLR
from data.data_queue import DataQueue
import numpy as np

class WILLR(Indicator):
    def __init__(self, params, name, scalingWindowSize, unstablePeriod, value):
        super().__init__(params, name, scalingWindowSize, unstablePeriod, value)
        period = self.params['period']
        self.high_values = DataQueue(maxlen=period)
        self.low_values = DataQueue(maxlen=period)
        self.close_values = DataQueue(maxlen=period)
        self.results = DataQueue(maxlen=self.windowSize)
    
    def compute(self, data):
        self.high_values.queue.append(data['high'])
        self.low_values.queue.append(data['low'])
        self.close_values.queue.append(data['close'])
        
        if len(self.high_values.queue) == self.params['period']:
            result = talib_WILLR(np.asarray(self.high_values.queue, dtype=np.float64), np.asarray(self.low_values.queue, dtype=np.float64), np.asarray(self.close_values.queue, dtype=np.float64), timeperiod=self.params['period'])[-1]
            self.results.addData(result)
            scaled_result = 0.5
            if self.results.curMax != self.results.curMin:
                scaled_result = (result - self.results.curMin) / (self.results.curMax - self.results.curMin)
            return {self.name: scaled_result}
        else:
            return {}