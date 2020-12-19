

from v2.strategy.strategies.strategy import Strategy


class buy_and_hold(Strategy):
    def calc_entry(self, data):
        return True

    def calc_exit(self, data):
        return False