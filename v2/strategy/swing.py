from v2.strategy.strategy import Strategy


class swing(Strategy):
    def __init__(self):
        self.indicators = ['close', 'sma_300']
        self.name = 'swing'
        self.is_ml = False
        self.diff = 0.03

    def get_param_ranges(self):
        params = {}
        params['diff'] = [0.01, 0.1, 0.01]
        
        return params

    def process(self, data):
        pass

    def calc_entry(self, data):
        if data.close < (data.sma_300 * (1- self.diff)):
            return True
        else:
            return False

    def calc_exit(self, data):
        if data.close > (data.sma_300 * (1 + self.diff)):
            return True
        else:
            return False
        
