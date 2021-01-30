
from dashboard.plot import DataStream


def initDataSreams(coins):
    data_streams = []
    portfolio_data = DataStream('portfolio')
    data_streams.append(portfolio_data)
    for coin in coins: 
        coin_data = DataStream(coin)
        data_streams.append(coin_data)

    return data_streams