

from indicators.indicator import Indicator
from talipp.indicators import SMA
from data.data_queue import DataQueue


class SMA(Indicator):
    def __init__(self, params, name, scalingWindowSize, value):
        super().__init__(params, name, scalingWindowSize, value)
        self.sma = SMA(period=self.params['period'])
        self.results = DataQueue()
    
    def compute(self, data):
        self.sma.add_input_value(data[self.input])
        if sma:
            result = sma[0]
            results.addData(result)
            scaled_result = 0.5
            if results.curMax != results.curMin:
                scaled_result = (result - results.curMin) / (results.curMax - results.curMin)
            return {self.name: scaled_result}
        else:
            return {}