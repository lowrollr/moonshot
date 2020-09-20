from v2.strategy.strategy import Strategy
import numpy as np
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression

class linear_reg(Strategy):
    def __init__(self):
        self.name = "Linear Regression"
        self.is_ml = True
        self.indicators = ['close', 'volume']
        self.target_forecast = ["close"]
        #predict out is by however many your step is in df
        #TODO add processing of the config again to have same step in minutes
        self.predict_out = 1
        self.model = ""

    def train(self, data):
        data["future_val"] = data[self.target_forecast].shift(-self.predict_out)
        data.drop(["trades", "high", "low"], axis=1, inplace=True)
        
        data.replace([np.inf, -np.inf], np.nan)
        data.dropna(inplace=True)
        X = np.array(data.drop("future_val", axis=1))[:-1]
        save_X = np.array(data.drop("future_val", axis=1))[-1]
        #X = np.array(data["close"])
        y = np.array(data["future_val"])[:-1]
        save_y = np.array(data.drop("future_val", axis=1))[-1]
        X = preprocessing.scale(X)
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.01, random_state=0)
        self.model = LinearRegression(n_jobs=-1)
        self.model.fit(X_train, y_train)
        print(self.model.predict([save_X]))
        pass

    def process(self, data):     
        # if data.
        pass

    def calc_entry(self, data):
        test = np.array([data])
        t = self.model.predict(test)
        if data.close < self.model.predict(np.array([data.close]).reshape(-1,1))[0] * 0.97:
            return True
        else:
            return False

    def calc_exit(self, data):
        if data.close > self.model.predict(np.array([data.close]).reshape(-1,1))[0] * 1.03:
            return True
        else:
            return False