import os
import sys

sys.path.append("../../../")

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import argrelextrema
from v2.model import Trading
from v2.strategy.indicators.smma import SMMA
from v2.strategy.indicators.stochastic_oscillator import StochasticOscillator
from v2.strategy.indicators.bollinger_bands import BollingerBands
from v2.strategy.indicators.rsi import RSI
from v2.strategy.indicators.macd import MACD
from v2.strategy.indicators.param import Param
import tensorflow as tf
import pickle
import warnings
warnings.filterwarnings('ignore')
from tqdm import tqdm
from sklearn.model_selection import train_test_split

def train_dir():
    if not os.path.isdir("./models"):
        os.system("mkdir models")
    if not os.path.exists("training_data.csv"):
        os.system("touch training_data.csv")
        with open("training_data.csv", "a") as f:
            f.write("model,score")

train_dir()

def load_config():
    my_config = {}
    with open('config.config') as config:
        for line in config:
            args = line.split('=')
            my_config[args[0]] = args[1].rstrip().split(',')
    return my_config

os.chdir('../../../')

print(os.getcwd())

model = Trading(load_config())

datasets = model.dfs
appended_dataset = pd.DataFrame()
for d in datasets:
    training_set = d[0]
    training_set['trough'] = training_set.iloc[argrelextrema(training_set.close.values, np.less_equal, order=480)[0]]['close']
    training_set['peak'] = training_set.iloc[argrelextrema(training_set.close.values, np.greater_equal, order=480)[0]]['close']
    ema_fast = Param(5, 10000, 0, 'ema_fast', 60)
    ema_slow= Param(6, 10001, 0, 'ema_slow', 120)
    signal = Param(5, 10001, 0, 'signal', 90)
    macd_ = MACD(_params=[ema_fast, ema_slow, signal], _name='macd')
    macd_.genData(training_set, gen_new_values=False)
    boll_period = Param(5, 10000, 0, 'period', 90)
    boll_bands = BollingerBands(_params=[boll_period], _name='bollinger_bands')
    boll_bands.genData(training_set, gen_new_values=False)
    stoch_highlow = Param(5, 10000, 0, 'highlow_range', 90.0)
    stoch_k = Param(5, 10000, 0, 'k_period', 270.0)
    stoch_oscillator = StochasticOscillator(_params=[stoch_highlow, stoch_k], _name='stochastic_oscillator')
    stoch_oscillator.genData(training_set, gen_new_values=False)
    rsi_period = Param(5, 10000, 0, 'period', 90.0)
    rsi_ = RSI(_params=[rsi_period], _name='rsi')
    rsi_.genData(training_set, gen_new_values=False)
    smma_period = Param(5, 10000, 0, 'period', 90.0)
    smma_ = SMMA(_params=[smma_period], _name='smma')
    smma_.genData(training_set, gen_new_values=False)
    training_set[['trough', 'peak']] = training_set[['trough', 'peak']].fillna(0)
    training_set['slope'] = (training_set['close'].rolling(window=30).max() - training_set['close'].rolling(window=30).min()) / training_set['close'].rolling(window=30).max()
    training_set = training_set.dropna()
    appended_dataset = appended_dataset.append(training_set)

train_df = appended_dataset[["time", "open", "high", "low", "close", "volume", "ema_slow", "ema_fast", "macd", "stosc_k", "rsi", "smma", "slope"]]
final_df = pd.DataFrame()
for i in range(1, 11):
    temp_df = train_df
    temp_df["predict_number"] = i
    temp_df["predict_forecast"] = temp_df["close"].shift(-int(i))
    final_df = pd.concat([final_df, temp_df])

final_df.dropna(inplace=True)
final_df.sort_values(by=['time'], inplace=True)

X = final_df.drop("predict_forecast", axis=1).values
y = final_df["predict_forecast"].values

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

from sklearn.linear_model import LinearRegression
from sklearn.linear_model import Ridge
from sklearn.linear_model import Lasso
from sklearn.linear_model import ElasticNet

#lin reg
lin_reg = LinearRegression(n_jobs=-1)
lin_reg.fit(X_train, y_train)
lin_reg_score = lin_reg.score(X_test, y_test)
pickle.dump(lin_reg, open('models/linear_reg.sav', 'wb'))
with open("training_data.csv", "a") as f:
    f.write("linear regression,{}".format(lin_reg_score))

#ridge
ridge = Ridge()
ridge.fit(X_train, y_train)
score = ridge.score(X_test, y_test)

pickle.dump(ridge, open('models/global_ridge.sav', 'wb'))
with open("training_data.csv", "a") as f:
    f.write("ridge_linear_model,{}".format(score))

#lasso
lasso = Lasso()
lasso.fit(X_train, y_train)
score = lasso.score(X_test, y_test)

pickle.dump(lasso, open('models/lasso.sav', 'wb'))
with open("training_data.csv", "a") as f:
    f.write("lasso_model,{}".format(score))

#e net
e_net = ElasticNet()
e_net.fit(X_train, y_train)
score = e_net.score(X_test, y_test)

pickle.dump(e_net, open('models/elastic_net.sav', 'wb'))
with open("training_data.csv", "a") as f:
    f.write("elastic_net,{}".format(score))

from sklearn.svm import SVR
from sklearn.svm import NuSVR
from sklearn.svm import LinearSVR

#SVR
svr_model = SVR()
svr_model.fit(X_train, y_train)
score = svr_model.score(X_test, y_test)

pickle.dump(svr_model, open('models/SVR.sav', 'wb'))
with open("training_data.csv", "a") as f:
    f.write("SVR,{}".format(score))

#NuSVR
n_svr_model = NuSVR()
n_svr_model.fit(X_train, y_train)
score = n_svr_model.score(X_test, y_test)

pickle.dump(n_svr_model, open('models/NuSVR.sav', 'wb'))
with open("training_data.csv", "a") as f:
    f.write("NuSVR,{}".format(score))

#Linear SVR
lin_svr = LinearSVR()
lin_svr.fit(X_train, y_train)
score = lin_svr.score(X_test, y_test)

pickle.dump(lin_svr, open('models/linear_SVR.sav', 'wb'))
with open("training_data.csv", "a") as f:
    f.write("linear_SVR,{}".format(score))

from sklearn.linear_model import SGDRegressor

#SGD
sgd_model = SGDRegressor()
sgd_model.fit(X_train, y_train)
score = sgd.score(X_test, y_test)

pickle.dump(sgd_model, open('models/SGD.sav', 'wb'))
with open("training_data.csv", "a") as f:
    f.write("SGD,{}".format(score))

from sklearn.neighbors import KNeighborsRegressor
from sklearn.neighbors import RadiusNeighborsRegressor

k_neigh_model = KNeighborsRegressor(n_jos=-1)
k_neigh_model.fit(X_train, y_train)
score = k_neigh_model(X_test, y_test)

pickle.dump(k_neigh_model, open('models/KNeighbors.sav', 'wb'))
with open("training_data.csv", "a") as f:
    f.write("KNeighbors,{}".format(score))

radius_model = RadiusNeighborsRegressor(n_jobs=-1)
radius_model.fit(X_train, y_train)
score = radius_model(X_test, y_test)

pickle.dump(radius_model, open('models/global_rad.sav', 'wb'))
with open("training_data.csv", "a") as f:
    f.write("Radius Neighbors,{}".format(score))

from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.ensemble import AdaBoostRegressor
from sklearn.ensemble import GradientBoostingRegressor
from xgboost import XGBRegressor

#RF regressor
rf_mod = RandomForestRegressor(n_jobs=-1)
rf_mod.fit(X_train, y_train)
score = rf_mod.score(X_test, y_test)

pickle.dump(rf_mod, open('models/random_forest.sav', 'wb'))
with open("training_data.csv", "a") as f:
    f.write("Random Forest,{}".format(score))

#Extra Forest regressor
ef_mod = ExtraTreesRegressor(n_jobs=-1)
ef_mod.fit(X_train, y_train)
score = ef_mod.score(X_test, y_test)

pickle.dump(ef_mod, open('models/extra_forest.sav', 'wb'))
with open("training_data.csv", "a") as f:
    f.write("Extra Forest,{}".format(score))

#ada regression
ada_mod = AdaBoostRegressor()
ada_mod.fit(X_train, y_train)
score = ada_mod.score(X_test, y_test)

pickle.dump(ada_mod, open('models/ada_regressor.sav', 'wb'))
with open("training_data.csv", "a") as f:
    f.write("Ada Forest,{}".format(score))

grad_mod = GradientBoostingRegressor()
grad_mod.fit(X_train, y_train)
score = grad_mod.score(X_test, y_test)

pickle.dump(grad_mod, open('models/grad_boost_sklearn.sav', 'wb'))
with open("training_data.csv", "a") as f:
    f.write("Sklearn Gradient Boost,{}".format(score))

boost_mod = XGBRegressor(n_jobs=-1)
boost_mod.fit(X_train, y_train)
score = boost_mod.score(X_test, y_test)

pickle.dump(boost_mod, open('models/grad_boost_orig.sav', 'wb'))
with open("training_data.csv", "a") as f:
    f.write("Grad boosting Original,{}".format(score))
