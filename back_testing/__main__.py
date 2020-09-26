from load_config import load_config
from v2.model import Trading
import os

if __name__ == '__main__':
    config = load_config()
    model = Trading(config)
    model.backtest()
