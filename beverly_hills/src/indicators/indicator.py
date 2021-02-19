import sys
from data.data_queue import DataQueue

class Indicator:
    def __init__(self, params, name, scalingWindowSize):
        self.params = params
        self.name = name
        self.windowSize = scalingWindowSize
        self.resultQueues = dict()

    

    def compute(self, data):
        # compute indicator, add to data queue, and return scaled result
        return

