from indicators.indicator import Indicator
from datetime import datetime
from data.data_queue import DataQueue


class MOH(Indicator):
    def __init__(self, params, name, scalingWindowSize, unstablePeriod, value):
        super().__init__(params, name, scalingWindowSize, unstablePeriod, value)
        
        self.results = DataQueue(maxlen=self.windowSize)
    
    def compute(self, data):
        result = datetime.fromtimestamp().minute
        self.results.addData(result)
        scaled_result = 0.5
        if self.results.curMax != self.results.curMin:
            scaled_result = (result - self.results.curMin) / (self.results.curMax - self.results.curMin)
        return {self.name: scaled_result}