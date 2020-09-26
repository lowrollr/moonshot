class Strategy:
    def __init__(self):
        self.indicators = []
        self.is_ml = False
    def process(self, data):
        # this happens every tick
        # use this to keep track of things that need to be kept track of over multiple ticks

        pass
        
    def getIndicators(self):
        return self.indicators
    def calc_entry(self, data):
        return 0.0
    def calc_exit(self, data):
        return 0.0
