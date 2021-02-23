from indicators.indicator import Indicator
from talib import BOP as talib_BOP
from data.data_queue import DataQueue


class BOP(Indicator):
    def __init__(self, params, name, scalingWindowSize, value):
        super().__init__(params, name, scalingWindowSize, value)
        
        self.results = DataQueue(maxlen=self.windowSize)
    
    def compute(self, data):
        result = talib_BOP(data['open'], data['high'], data['low'], data['close'])[-1]
        results.addData(result)
        scaled_result = 0.5
        if results.curMax != results.curMin:
            scaled_result = (result - results.curMin) / (results.curMax - results.curMin)
        return {self.name: scaled_result}
        