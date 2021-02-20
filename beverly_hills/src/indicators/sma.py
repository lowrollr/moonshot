

from indicators.indicator import Indicator
from talipp.indicators import SMA
from data.data_queue import DataQueue


class SMA(Indicator):
    def __init__(self, params, name, scalingWindowSize, input_value):
        super().__init__(params, name, scalingWindowSize)
        self.sma = SMA(period=self.params['period'])
        self.results = DataQueue()
        self.input = input_value
    
    def compute(self, data):
        self.sma.add_input_value(data[self.input])
        if sma:
            result = sma[0]
            results.append(result)
            scaled_result = 0.5
            if results.curMax != results.curMin:
                scaled_result = (result - results.curMin) / (results.curMax - results.curMin)
            return {self.name: scaled_result}
        else:
            return {}