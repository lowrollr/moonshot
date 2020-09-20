from v2.strategy.strategy import Strategy


class swing(Strategy):
    def __init__(self):
        self.indicators = ['close', 'sma_300']

    def process(self, data):
        pass

    def calc_entry(self, data):
        if data.close < (data.sma_300 * 0.97):
            return True
        else:
            return False

    def calc_exit(self, data):
        if data.close > (data.sma_300 * 1.03):
            return True
        else:
            return False
        
