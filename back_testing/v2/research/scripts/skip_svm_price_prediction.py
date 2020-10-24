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
    if not os.path.exists("training_data.csv"):
        os.system("touch training_data.csv")
        with open("training_data.csv", "a") as f:
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

print("now training models\n")

from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.ensemble import AdaBoostRegressor
from sklearn.ensemble import GradientBoostingRegressor

grad_mod = GradientBoostingRegressor()
grad_mod.fit(X_train, y_train)
score = grad_mod.score(X_test, y_test)

pickle.dump(grad_mod, open('v2/research/scripts/models/grad_boost_sklearn.sav', 'wb+'))
with open("v2/research/scripts/training_data.csv", "a") as f:
    f.write("Sklearn Gradient Boost,{}\n".format(score))
