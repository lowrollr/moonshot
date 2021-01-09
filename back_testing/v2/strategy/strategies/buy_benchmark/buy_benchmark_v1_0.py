

from v2.strategy.strategies.strategy import Strategy
import numpy as np



class Benchmark(Strategy):
    def __init__(self, scaler, buy_model, buy_model_features,):
        print('Running benchmark...')
        self.is_ml = False
        self.name = 'benchmark'
        self.scaler = scaler
        self.buy_model = buy_model
        
        self.indicators = []
        self.buy_model_features = buy_model_features
        
        self.looking_for_entry = False
        self.looking_for_exit = False

    def process(self, data):
        if self.looking_for_exit:
            self.stop_loss = max(self.stop_loss, 0.9995 * data.close)
        elif self.looking_for_entry:
            self.trailing_entry = min(self.trailing_entry, 1.0005 * data.close)

    def calc_entry(self, data):
        if self.looking_for_entry and (data.close > self.trailing_entry):
            self.looking_for_entry = False
            return True
        buy_model_data = np.array([getattr(data, x) for x in self.buy_model_features])
        buy_model_data = buy_model_data.reshape(1, -1)
        buy_model_data = self.scaler.transform(buy_model_data)
        prediction = self.buy_model.predict(buy_model_data)[0]

        if prediction:
            self.looking_for_entry = True
            self.trailing_entry = 1.0005 * data.close
        return False

    def calc_exit(self, data):
        if (data.close < self.stop_loss):
            self.looking_for_exit = False
            return True
        return False