from v2.strategy.indicators.indicator import Indicator
from pyti.exponential_moving_average import exponential_moving_average as ema
import pandas

class EMA(Indicator):
    
    def genData(self, dataset, gen_new_values=True, value='close'):
        #assumes that the first param is the sma period
        #some indicators require that param names are ascribed correctly
        period = self.params[0]
        if gen_new_values:
            period.genValue()

        # dataset[self.name] = ema(dataset[value].tolist(), period.value)
        dataset[self.name] = dataset[value].ewm(span=period.value, adjust=False).mean()