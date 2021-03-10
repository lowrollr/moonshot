from indicators.indicator import Indicator
from datetime import datetime
from data.data_queue import DataQueue, MinMax2LayerDataQueue
from sys import maxsize
from math import sqrt, acos


class JTI(Indicator):
    def __init__(self, params, name, scalingWindowSize, unstablePeriod, value):
        super().__init__(params, name, scalingWindowSize, unstablePeriod, value)
        self.lookingForMax = True
        self.curMin = (maxsize, 0)
        self.curMax = (0, 0)
        self.lastMin = (maxsize, 0)
        self.lastMax = (0, 0)
        self.results = dict()
        self.results['a'] = DataQueue(maxlen=self.windowSize)
        self.results['b'] = DataQueue(maxlen=self.windowSize)
        self.results['c'] = DataQueue(maxlen=self.windowSize)
        self.results['theta'] = DataQueue(maxlen=self.windowSize)
    
    def compute(self, data):
        cur_time = data.time
        cur_value = getattr(data, self.value)
        if self.lookingForMax:
            
            if self.curMin[1] and self.lastMax[1]:
                minutes_since_max = int((cur_time - self.lastMax[1]) / 60)
                minutes_since_min = int((cur_time - self.curMin[1]) / 60)
                minutes_since_between = int((self.curMin[1] - self.lastMax[1]) / 60)
                jti_a = sqrt(pow(minutes_since_min, 2) + pow((1 - (self.curMin[0]/data.close)), 2))
                jti_b = sqrt(pow(minutes_since_max, 2) + pow((1 - (self.lastMax[0]/data.close)), 2))
                jti_c = sqrt(pow(minutes_since_min, 2) + pow((1 - (self.lastMax[0]/self.curMin[0])), 2))
                cos_c = (pow(jti_a, 2) + pow(jti_b, 2) - pow(jti_c, 2)) / (2 * jti_a * jti_b)
                jti_theta = 0.0
                try:
                    jti_theta = acos(cos_c)
                except ValueError as err:
                    jti_theta = 0.0

                self.results['a'].addData(jti_a)
                self.results['b'].addData(jti_b)
                self.results['c'].addData(jti_c)
                self.results['theta'].addData(jti_theta)

            if cur_value < self.curMax[0]:
                self.lookingForMax = False
                self.lastMin = self.curMin
                self.curMin = (cur_value, cur_time)
            else:
                self.computecurMax = (cur_value, cur_time)
        else:
            if self.curMax[1] and self.lastMin[1]:
                minutes_since_max = int((cur_time - self.curMax[1]) / 60000)
                minutes_since_min = int((cur_time - self.lastMin[1]) / 60000)
                minutes_between = int((self.curMax[1] - self.lastMin[1]) / 60000)
                jti_a = sqrt(pow(minutes_since_max, 2) + pow((1 - (self.curMax[0]/data.close)), 2))
                jti_b = sqrt(pow(minutes_since_min, 2) + pow((1 - (self.lastMin[0]/data.close)), 2))
                jti_c = sqrt(pow(minutes_between, 2) + pow((1 - (self.lastMin[0]/self.curMax[0])), 2))
                cos_c = (pow(jti_a, 2) + pow(jti_b, 2) - pow(jti_c, 2)) / (2 * jti_a * jti_b)

                jti_theta = 0.0
                try:
                    jti_theta = acos(cos_c)
                except ValueError as err:
                    jti_theta = 0.0
                
                self.results['a'].addData(jti_a)
                self.results['b'].addData(jti_b)
                self.results['c'].addData(jti_c)
                self.results['theta'].addData(jti_theta)

            if cur_value > self.curMin[0]:
                self.lookingForMax = True
                self.lastMax = self.curMax
                self.curMax = (cur_value, cur_time)
            else:
                self.curMin = (cur_value, cur_time)

        results_to_return = dict()
        default_result = 0.5
        for item in {'a', 'b', 'c', 'theta'}:
            if self.results[item].curMax != self.results[item].curMin:
                results_to_return[f'{self.name}_{item}'] = (self.results[item][-1] - self.results[item].curMin) / (self.results[item].curMax - self.results[item].curMin)
            else:
                results_to_return[f'{self.name}_{item}'] = default_result
                
        return results_to_return