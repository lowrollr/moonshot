import fileinput


filenames = ['./BTCUSD/Candles_1m/2013/merged.csv', './BTCUSD/Candles_1m/2014/merged.csv', './BTCUSD/Candles_1m/2015/merged.csv', './BTCUSD/Candles_1m/2016/merged.csv', './BTCUSD/Candles_1m/2017/merged.csv', './BTCUSD/Candles_1m/2018/merged.csv','./BTCUSD/Candles_1m/2019/merged.csv']
with open('merged_BTC.csv', 'w') as fout, fileinput.input(filenames) as fin:
    for line in fin:
        fout.write(line)