from v2.strategy.strategies.strategy import Strategy
from v2.strategy.indicators.param import Param
from v2.strategy.indicators.indicator import Indicator
import numpy as np
from sklearn import preprocessing
from v2.strategy.indicators.smma import SMMA
from v2.strategy.indicators.macd import MACD
from sklearn.ensemble import RandomForestRegressor

def warn(*args, **kwargs):
    pass
import warnings
warnings.warn = warn

class linear_reg(Strategy):
    def __init__(self):
        self.name = "Linear Regression"
        self.is_ml = True
        self.inputs = ["MACD", "signal", "close", "time", "sma"]

        #add some checking between the params
        self.predict_out = Param(1, 300, 0, "predict", 15)
        self.train_on = Param(1500, 1500, 0, "train_on", 1500)
        self.update_num = Param(2, 10000, 0, "update_num", 100)
        self.diff = Param(0.003, 0.1, 3, 'diff', 0.01)
        self.model = ""
        sma_period = Param(37, 37, 0, "sma", 37)
        ema_fast = Param(5, 10000, 0, 'ema_fast', 15)
        ema_slow= Param(6, 10001, 0, 'ema_slow', 500)
        signal = Param(5, 10001, 0, 'signal', 500)

        self.indicators = [MACD(_params=[ema_fast, ema_slow, signal]), SMMA(_params=[sma_period], _name='sma'), Indicator(_params=[self.diff, self.train_on], _name='diff')]
        
        self.counter = 0

    def train(self, data):
        pass

    def process(self, data, full_data): 
        if self.counter % int(self.update_num.value) == 0:
            #get dataset
            # filtered_time_df = full_data[["close", "time"]]
            filtered_time_df = full_data.loc[(full_data["time"] < data.time)].sort_values(by=['time'])
            reduced_df = filtered_time_df
            if len(filtered_time_df) >= self.train_on.value:
                reduced_df = filtered_time_df.head(int(self.train_on.value))
            #add future val
            reduced_df = reduced_df[[name for name in self.inputs]]
            reduced_df["future_val"] = reduced_df["close"].shift(- int(self.predict_out.value))

            #get rid of infinities and nan if there are
            reduced_df.replace([np.inf, -np.inf], np.nan)
            reduced_df.dropna(inplace=True)

            X = np.array(reduced_df.drop("future_val", axis=1))
            y = np.array(reduced_df["future_val"])

            self.model = RandomForestRegressor(n_jobs=-1)
            self.model.fit(X, y)
            self.counter = 0
        self.counter += 1

    def calc_entry(self, data):
        test = np.array([[getattr(data, name) for name in self.inputs]])
        t = self.model.predict(test)
        if data.close < t[0] * (1 - self.diff.value):
            return True
        else:
            return False

    def calc_exit(self, data):
        test = np.array([[getattr(data, name) for name in self.inputs]])
        t = self.model.predict(test)
        if data.close > t[0] * (1 + self.diff.value):
            return True
        else:
            return False

    def get_param_ranges(self):
        return dict()