from indicators.indicator import Indicator
from talipp.indicators import CCI
from data.data_queue import DataQueue


class CCI(Indicator):
    def __init__(self, params, name, scalingWindowSize, value):
        super().__init__(params, name, scalingWindowSize, value)
        self.cci = CCI(period=self.params['period'])
        self.results = DataQueue()
    
    def compute(self, data):
        self.cci.add_input_value(data[self.input])
        if cci:
            result = cci[0]
            results.addData(result)
            scaled_result = 0.5
            if results.curMax != results.curMin:
                scaled_result = (result - results.curMin) / (results.curMax - results.curMin)
            return {self.name: scaled_result}
        else:
            return {}