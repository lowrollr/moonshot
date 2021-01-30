import pandas as pd
import numpy as np
import os
import sys

coin = sys.argv[1].upper()
filename = f'{coin}USDT-1m-data.csv'
timestamp_label = 'close_time'
good_amount = 64800

data = pd.read_csv(f'../binance/{filename}')
data.reset_index(inplace=True)
data['diff'] = data[timestamp_label].diff()
data['diff'] = data['diff'].shift(1)
gaps = data[data['diff'] >= 120000]['index'].values
data.dropna(inplace=True)
cur_chunk_start = 0
chunk_num = 1
for x in gaps:
    chunk_size = x - cur_chunk_start
    if chunk_size > good_amount:
        chunk = data.iloc[cur_chunk_start:x+1][['close_time', 'open', 'high', 'low', 'close', 'volume']]
        if not os.path.isdir(f'../binance/{coin}/1m/'):
            os.makedirs(f'../binance/{coin}/1m/')
        chunk.to_csv(f'../binance/{coin}/1m/{coin}USDT-1m-data_chunk' + '0'*(6 -len(str(chunk_num))) + str(chunk_num) + '.csv')
        chunk_num += 1
    cur_chunk_start = x + 2
