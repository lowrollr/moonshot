

class Indicator:
    def __init__(self, params, name, scalingWindowSize):
        self.name = name
        self.params = params
        self.windowSize = scalingWindowSize
        self.resultQueues = dict()

    

    def compute(self, data):
        # compute indicator, add to data queue, and return scaled result
        return {}

