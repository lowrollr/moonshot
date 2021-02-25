

class Indicator:
    def __init__(self, params, name, scalingWindowSize, unstablePeriod, value):
        self.name = name
        self.params = params
        self.windowSize = scalingWindowSize
        self.minUnstablePeriod = unstablePeriod
        self.value = value

    

    def compute(self, data):
        # compute indicator, add to data queue, and return scaled result
        return {}

