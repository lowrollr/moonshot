import random

class Param:
    def __init__(self, _low, _up, _prec, _name):
        self.low = _low
        self.up = _up
        self.prec = _prec
        self.value = self.low
        self.name = _name
    
    def shrinkRange(self, center, percentage):
        delta = self.up - self.low
        new_low = max(self.low, center - (percentage * delta))
        new_up = min(self.up, center + (percentage * delta))
        self.low = new_low
        self.up = new_up

    def genValue(self):
        self.value = round(random.uniform(self.low, self.up), self.prec)
        return self.value