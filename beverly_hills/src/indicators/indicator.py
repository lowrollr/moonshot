

class Indicator:
    def __init__(self, params, name, scalingWindowSize, value):
        self.name = name
        self.params = params
        self.windowSize = scalingWindowSize
        self.value = value

    

    def compute(self, data):
        # compute indicator, add to data queue, and return scaled result
        return {}

