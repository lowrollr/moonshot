from indicators.indicator import Indicator
from talib import CCI as talib_CCI
from data.data_queue import DataQueue


class CCI(Indicator):
    def __init__(self, params, name, scalingWindowSize, value):
        super().__init__(params, name, scalingWindowSize, value)
        period = self.params['period']
        self.high_values = DataQueue(maxlen=period)
        self.low_values = DataQueue(maxlen=period)
        self.close_values = DataQueue(maxlen=period)
        self.results = DataQueue(maxlen=self.windowSize)
    
    def compute(self, data):
        self.high_values.queue.append(data['high'])
        self.low_values.queue.append(data['low'])
        self.close_values.queue.append(data['up'])
        
        if len(self.high_values.queue) == self.params['period']:
            result = talib_CCI(self.high_values.queue, self.low_values.queue, self.close_values.queue, timeperiod=self.params['period'])[-1]
            results.addData(result)
            scaled_result = 0.5
            if results.curMax != results.curMin:
                scaled_result = (result - results.curMin) / (results.curMax - results.curMin)
            return {self.name: scaled_result}
        else:
            return {}