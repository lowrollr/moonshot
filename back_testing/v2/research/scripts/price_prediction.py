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
lin_reg = LinearRegression()
lin_reg.fit(X_train, y_train)
print(lin_reg.score(X_test, y_test))

#ridge
alphas = [0.01, 0.05, 0.075]
max_score = 0
alpha_val = 0
global_ridge = 0
for a in tqdm(alphas):
    ridge = Ridge(alpha=a)
    ridge.fit(X_train, y_train)
    score = ridge.score(X_test, y_test)
    if score > max_score:
        alpha_val = a
        max_score = score
        global_ridge = ridge

print("Max score is: {} with alpha of: {}".format(max_score, alpha_val))

#lasso
alphas = [0.01, 0.1, 0.5]
max_score = 0
alpha_val = 0
global_lasso = 0
for a in tqdm(alphas):
    lasso = Lasso(alpha=a)
    lasso.fit(X_train, y_train)
    score = lasso.score(X_test, y_test)
    if score > max_score:
        alpha_val = a
        max_score = score
        global_lasso = lasso

print("Max score is: {} with alpha of: {}".format(max_score, alpha_val))

#multi task lasso
alphas = [0.01, 0.1, 0.5, 1, 2]
l1_ratio = [0.01, 0.1, 0.3, 0.5]
max_score = 0
alpha_val = 0
l1_value = 0
global_e_net = 0
for a in tqdm(alphas):
    for l in l1_ratio:
        e_net = ElasticNet(alpha=a, l1_ratio=l)
        e_net.fit(X_train, y_train)
        score = e_net.score(X_test, y_test)
        if score > max_score:
            alpha_val = a
            l1_value = l
            max_score = score
            global_e_net = e_net

print("Max score is: {} with alpha of: {} and l1 val of: {}".format(max_score, alpha_val, l1_value))

from sklearn.svm import SVR
from sklearn.svm import NuSVR
from sklearn.svm import LinearSVR

#SVR
kernels = ['linear', 'poly', 'rbf', 'sigmoid', 'precomputed']
degrees = [1, 5, 7]
C_vals = [0.1, 0.5, 0.7, 1, 2]
max_score = 0
ker_val = "rbf"
deg_val = 3
C_val = 1
global_svr = 0

for k in tqdm(kernels):
    svr_model = SVR(kernel=k)
    svr_model.fit(X_train, y_train)
    score = svr_model.score(X_test, y_test)
    if score > max_score:
        max_score = score
        ker_val = k
        global_svr = svr_model

for d in tqdm(degrees):
    svr_model = SVR(kernel=ker_val, degree=d)
    svr_model.fit(X_train, y_train)
    score = svr_model.score(X_test, y_test)
    if score > max_score:
        max_score = score
        deg_val = d
        global_svr = svr_model

for c in tqdm(C_vals):
    svr_model = SVR(kernel=ker_val, degree=deg_val, C=c)
    svr_model.fit(X_train, y_train)
    score = svr_model.score(X_test, y_test)
    if score > max_score:
        max_score = score
        C_val = c
        global_svr = svr_model

print("Max score is: {} with kernel of: {}, degree val of: {}, and c_val of: {}".format(max_score, ker_val, deg_val, C_val))

#NuSVR
kernels = ['linear', 'poly', 'sigmoid', 'precomputed']
degrees = [1, 5, 7]
C_vals = [0.1, 0.5, 0.7, 2]
nus = [0.1, 0.3, 0.5, 0.7, 1]

max_score = 0
ker_val = 'rbf'
deg_val = 3
C_val = 1
nu_val = 0.5
global_n_svr = 0

for n in tqdm(nus):
    n_svr_model = NuSVR(nu=n)
    n_svr_model.fit(X_train, y_train)
    score = n_svr_model.score(X_test, y_test)
    if score > max_score:
        max_score = score
        nu_val = n
        global_n_svr = n_svr_model

for k in tqdm(kernels):
    n_svr_model = NuSVR(nu=nu_val, kernel=k)
    n_svr_model.fit(X_train, y_train)
    score = n_svr_model.score(X_test, y_test)
    if score > max_score:
        max_score = score
        ker_val = k
        global_n_svr = n_svr_model

for c in tqdm(C_vals):
    n_svr_model = NuSVR(C=c, nu=nu_val, kernel=ker_val)
    n_svr_model.fit(X_train, y_train)
    score = n_svr_model.score(X_test, y_test)
    if score > max_score:
        max_score = score
        C_val = c
        global_n_svr = n_svr_model

for d in tqdm(degrees):
    n_svr_model = NuSVR(C=C_val, nu=nu_val, kernel=ker_val, degree=d)
    n_svr_model.fit(X_train, y_train)
    score = n_svr_model.score(X_test, y_test)
    if score > max_score:
        max_score = score
        deg_val = d
        global_n_svr = n_svr_model
                    
print("Max score is: {} with kernel of: {}, degree val of: {}, and c_val of: {}".format(max_score, ker_val, deg_val, C_val))

#Linear SVR
losses = ['epsilon_insensitive', 'squared_epsilon_insensitive']
C_values = [0.1, 0.5, 0.7, 1, 2]

max_score = 0
loss_val = ""
deg_val = 0
C_val = 0
global_lin_svr = 0

for l in tqdm(losses):
    lin_svr = LinearSVR(loss=l)
    lin_svr.fit(X_train, y_train)
    score = lin_svr.score(X_test, y_test)
    if score > max_score:
        max_score = score
        loss_val = l
        global_lin_svr = lin_svr

for c in tqdm(C_values):
    lin_svr = LinearSVR(loss=loss_val, C=c)
    lin_svr.fit(X_train, y_train)
    score = lin_svr.score(X_test, y_test)
    if score > max_score:
        max_score = score
        C_val = c
        global_lin_svr = lin_svr

print("Max score is: {} with loss of: {} and c_val of: {}".format(max_score, loss_val, C_val))

from sklearn.linear_model import SGDRegressor

#SGD
losses = ['squared_loss', 'huber', 'epsilon_insensitive','squared_epsilon_insensitive']
alphas = [0.0001, 0.01, 0.1, 0.5, 0.9]
l1_ratios = [0.01, 0.15, 0.3, 0.5, 0.8]

max_score = 0
alph = 0.0001
l1_rat = 0.15
loss_val = ""
global_sgd = 0

for l in tqdm(losses):
    for a in alphas:
        for r in l1_ratios:
            sgd_model = SGDRegressor(loss=l, alpha=a, l1_ratio=r)
            sgd_model.fit(X_train, y_train)
            score = sgd.score(X_test, y_test)
            if score > max_score:
                max_score = score
                loss_val = l
                alph = a
                l1_rat = r
                global_sgd = sgd_model

print("Max score is: {} with loss of: {}, alpha of: {}, and l1 ratio of: {}".format(max_score, loss_val, alph, l1_rat))

from sklearn.neighbors import KNeighborsRegressor
from sklearn.neighbors import RadiusNeighborsRegressor

neighbors = [1, 5, 10, 20]
leaf_sizes = [2, 5, 15, 30, 60]

max_score = 0
leaf_val = 0
neighbor_val = 0
global_k_neighbor = 0

for l in tqdm(leaf_sizes):
    for n in neighbors:
        k_neigh_model = KNeighborsRegressor(n_neighbors=n, leaf_size=l, n_jobs=-1)
        k_neigh_model.fit(X_train, y_train)
        score = k_neigh_model(X_test, y_test)
        if score > max_score:
            max_score = score
            neighbor_val = n
            leaf_val = l
            global_k_neighbor = k_neigh_model

print("Max score is: {} with {} nieghbors, and a leaf size of: {}".format(max_score, neighbor_val, leaf_val))

radius= [.1, .5, 1, 2, 10]
leaf_sizes = [2, 5, 15, 30, 60]

max_score = 0
leaf_val = 0
rad_val = 0
global_rad = 0

for l in tqdm(leaf_sizes):
    for r in radius:
        radius_model = RadiusNeighborsRegressor(radius=r, leaf_size=l, n_jobs=-1)
        radius_model.fit(X_train, y_train)
        score = radius_model(X_test, y_test)
        if score > max_score:
            max_score = score
            rad_val = r
            leaf_val = l
            global_rad = radius_model

print("Max score is: {} with {} nieghbors, and a leaf size of: {}".format(max_score, rad_val, leaf_val))

from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.ensemble import AdaBoostRegressor
from sklearn.ensemble import GradientBoostingRegressor
from xgboost import XGBRegressor



print('hi')
