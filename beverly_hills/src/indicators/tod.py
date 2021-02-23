from indicators.indicator import Indicator
from datetime import datetime
from data.data_queue import DataQueue


class TOD(Indicator):
    def __init__(self, params, name, scalingWindowSize, value):
        super().__init__(params, name, scalingWindowSize, value)
        
        self.results = DataQueue(maxlen=self.windowSize)
    
    def compute(self, data):
        result = datetime.fromtimestamp().hour
        results.addData(result)
        scaled_result = 0.5
        if results.curMax != results.curMin:
            scaled_result = (result - results.curMin) / (results.curMax - results.curMin)
        return {self.name: scaled_result}