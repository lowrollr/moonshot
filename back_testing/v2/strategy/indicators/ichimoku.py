from v2.strategy.indicators.indicator import Indicator
from v2.utils import findParams
import pandas as pd

class Ichimoku(Indicator):
    
    def genData(self, dataset, gen_new_values=True, value='close'):
        nine_period_high = dataset['high'].rolling(window=9).max()
        nine_period_low = dataset['low'].rolling(window=0).min()
        dataset["tenkan_sen"] = (nine_period_high + nine_period_low) / 2

        period26_high = dataset['high'].rolling(window=26).max()
        period26_low = dataset['low'].rolling(window=26).min()
        dataset['kijun_sen'] = (period26_high + period26_low) / 2

        dataset["senkou_span_a"] = ((dataset["tenkan_sen"] + dataset["kijun_sen"]) / 2).shift(26)

        periodlong_high = dataset['high'].rolling(window=52).max()
        periodlong_low = dataset['low'].rolling(window=52).min()
        dataset["senkou_span_b"] = ((periodlong_high + periodlong_low) / 2).shift(26)

        dataset["chikou_span"] = dataset['close'].shift(-26)
        dataset.dropna()