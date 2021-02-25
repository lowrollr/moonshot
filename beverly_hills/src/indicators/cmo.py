from indicators.indicator import Indicator
from talib import CMO as talib_CMO
from data.data_queue import DataQueue
import numpy as np


class CMO(Indicator):
    def __init__(self, params, name, scalingWindowSize, unstablePeriod, value):
        super().__init__(params, name, scalingWindowSize, unstablePeriod, value)
        period = self.params['period']
        self.values = DataQueue(maxlen=max(self.minUnstablePeriod, period + 1))
        self.results = DataQueue(maxlen=self.windowSize)
    
    
    def compute(self, data):
        self.values.queue.append(data[self.value])
        
        
        if len(self.values.queue) >= self.params['period'] + 1:
            result = talib_CMO(np.asarray(self.values.queue, dtype=np.float64), timeperiod=self.params['period'])[-1]
            self.results.addData(result)
            scaled_result = 0.5
            if self.results.curMax != self.results.curMin:
                scaled_result = (result - self.results.curMin) / (self.results.curMax - self.results.curMin)
            return {self.name: scaled_result}
        else:
            return {}