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
import pickle
import warnings
warnings.filterwarnings('ignore')
from tqdm import tqdm
from sklearn.model_selection import train_test_split

def train_dir():
    if not os.path.isdir("./models"):
        os.system("mkdir models")
    if not os.path.isdir("./graphs"):
        os.system("mkdir graphs")
    with open("training_data.csv", "w") as f:
        f.write("model,score\n")

train_dir()

os.chdir('../../../')

def load_config():
    my_config = {}
    with open('config.config') as config:
        for line in config:
            args = line.split('=')
            my_config[args[0]] = args[1].rstrip().split(',')
    return my_config

model = Trading(load_config())

print("loading data...")

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

train_df = appended_dataset[["time", "close", "volume", "macd", "stosc_k", "rsi", "smma", "slope"]]
final_df = pd.DataFrame()
PREDICT_NUM = 5
predics = [5, 10, 25, 50, 100]
for i in predics:
    temp_df = train_df
    temp_df["predict_number"] = i
    temp_df["predict_forecast"] = temp_df["close"].shift(-int(i))
    final_df = pd.concat([final_df, temp_df])

final_df.dropna(inplace=True)
final_df.sort_values(by=['time'], inplace=True)

X = final_df.drop("predict_forecast", axis=1).values
y = final_df["predict_forecast"].values

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

graph_X = []
graph_X_pred = []
graph_y = []
for i in range(len(X_test)):
    if X_test[i][-1] == PREDICT_NUM:
        graph_X.append(X_test[i][0])
        graph_X_pred.append(X_test[i])
        graph_y.append(y_test[i])
print("now training models\n")

graph_X = graph_X[-1440:] 
graph_X_pred = graph_X_pred[-1440:]
graph_y = graph_y[-1440:]
future_graph_X = [x + PREDICT_NUM for x in graph_X]

from sklearn.linear_model import LinearRegression
from sklearn.linear_model import Ridge
from sklearn.linear_model import Lasso
from sklearn.linear_model import ElasticNet
from xgboost import XGBRegressor

#lin reg
grad_boost = LinearRegression(n_jobs=-1)
grad_boost.fit(X_train, y_train)
lin_reg_score = grad_boost.score(X_test, y_test)
pickle.dump(grad_boost, open('v2/research/scripts/models/xgboost.sav', 'wb+'))
with open("v2/research/scripts/training_data.csv", "a") as f:
    f.write("grad boost,{}\n".format(lin_reg_score))
predictions = grad_boost.predict(graph_X_pred)
plt.plot(future_graph_X, graph_y, label = "original prices", color="blue")
plt.plot(graph_X, predictions, label = "predicted prices", color="red")
plt.savefig('v2/research/scripts/graphs/xgbregrossor.png')
plt.clf()

test_y = [7150] * 1440

#lin reg
lin_reg = LinearRegression(n_jobs=-1)
lin_reg.fit(X_train, y_train)
lin_reg_score = lin_reg.score(X_test, y_test)
pickle.dump(lin_reg, open('v2/research/scripts/models/linear_reg.sav', 'wb+'))
with open("v2/research/scripts/training_data.csv", "a") as f:
    f.write("linear regression,{}\n".format(lin_reg_score))
predictions = lin_reg.predict(graph_X_pred)
plt.plot(future_graph_X, test_y, label = "original prices", color="blue")
plt.plot(graph_X, test_y, label = "predicted prices", color="red")
plt.savefig('v2/research/scripts/graphs/lin_reg.png')
plt.clf()

#ridge
ridge = Ridge(alpha = .01)
ridge.fit(X_train, y_train)
score = ridge.score(X_test, y_test)

pickle.dump(ridge, open('v2/research/scripts/models/global_ridge.sav', 'wb+'))
with open("v2/research/scripts/training_data.csv", "a") as f:
    f.write("ridge_linear_model,{}\n".format(score))
predictions = ridge.predict(graph_X_pred)
plt.plot(future_graph_X, graph_y, label = "original prices", color="blue")
plt.plot(graph_X, predictions, label = "predicted prices", color="red")
plt.savefig('v2/research/scripts/graphs/ridge.png')
plt.clf()

#lasso
lasso = Lasso()
lasso.fit(X_train, y_train)
score = lasso.score(X_test, y_test)

pickle.dump(lasso, open('v2/research/scripts/models/lasso.sav', 'wb+'))
with open("v2/research/scripts/training_data.csv", "a") as f:
    f.write("lasso_model,{}\n".format(score))
predictions = lasso.predict(graph_X_pred)
plt.plot(future_graph_X, graph_y, label = "original prices", color="blue")
plt.plot(graph_X, predictions, label = "predicted prices", color="red")
plt.savefig('v2/research/scripts/graphs/lasso.png')
plt.clf()

#e net
e_net = ElasticNet()
e_net.fit(X_train, y_train)
score = e_net.score(X_test, y_test)

pickle.dump(e_net, open('v2/research/scripts/models/elastic_net.sav', 'wb+'))
with open("v2/research/scripts/training_data.csv", "a") as f:
    f.write("elastic_net,{}\n".format(score))
predictions = e_net.predict(graph_X_pred)
plt.plot(future_graph_X, graph_y, label = "original prices", color="blue")
plt.plot(graph_X, predictions, label = "predicted prices", color="red")
plt.savefig('v2/research/scripts/graphs/e_net.png')
plt.clf()

from sklearn.ensemble import GradientBoostingRegressor

grad_mod = GradientBoostingRegressor()
grad_mod.fit(X_train, y_train)
score = grad_mod.score(X_test, y_test)

pickle.dump(grad_mod, open('v2/research/scripts/models/grad_boost_sklearn.sav', 'wb+'))
with open("v2/research/scripts/training_data.csv", "a") as f:
    f.write("Sklearn Gradient Boost,{}\n".format(score))
predictions = grad_model.predict(graph_X_pred)
plt.plot(future_graph_X, graph_y, label = "original prices", color="blue")
plt.plot(graph_X, predictions, label = "predicted prices", color="red")
plt.savefig('v2/research/scripts/graphs/grad_boost_sklearn.png')
plt.clf()
