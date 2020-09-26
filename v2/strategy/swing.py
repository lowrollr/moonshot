from v2.strategy.strategy import Strategy


class swing(Strategy):
    def __init__(self):
        self.sma = 60
        self.name = 'swing'
        self.is_ml = False
        self.diff = 0.03

    def get_param_ranges(self):
        params = {}
        # low bound / upper bound / step / is an indicator?
        # all numbers must be floats
        params['diff'] = [0.01, 0.1, 0.01, False]
        params['sma'] = [5.0, 10000.0, 5.0, True]
        return params
    
    def get_compond_params(self):
        compound_params = {}

        return compound_params

    def process(self, data):
        pass

    def calc_entry(self, data):
        if data.close < (data.sma * (1- self.diff)):
            return True
        else:
            return False

    def calc_exit(self, data):
        if data.close > (data.sma * (1 + self.diff)):
            return True
        else:
            return False
        
