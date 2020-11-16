'''
FILE: load_config.py
AUTHORS:
    -> Jacob Marshall (marshingjay@gmail.com)
WHAT:
    -> Default entry point for running the backtesting infrastructure
'''

from load_config import load_config

from v2.model import Trading

'''
ARGS:
    -> None
RETURN:
    -> None
WHAT: 
    -> Loads configuration, initiates Trading model, starts backtest procedure
'''
def run_app():
    config = load_config()
    model = Trading(config)
    model.backtest()