from load_config import load_config
from v2.model import Trading

def run_app():
    config = load_config()
    model = Trading(config)
    model.backtest()