from v2.strategy.indicators.indicator import Indicator
from v2.utils import findParams
from v2.strategy.indicators.sma import SMA
import pandas

class StochasticOscillator(Indicator):
    
    def genData(self, dataset, gen_new_values=True, value='close'):
        param_highlow_range, param_k_period_sma = findParams(self.params, ['highlow_range', 'k_period'])
        if gen_new_values:
            highlow_range_value = param_highlow_range.genValue()
            param_k_period_sma.up = highlow_range_value

        dataset['stosc_high_price'] = dataset['low'].rolling(window=int(highlow_range_value)).min()
        dataset['stosc_low_price'] = dataset['high'].rolling(window=int(highlow_range_value)).max()
        dataset['stosc_k'] = 100*((dataset['close'] - dataset['stosc_low_price']) / (dataset['stosc_high_price'] - dataset['stosc_low_price']))

        k_period_sma = SMA([param_k_period_sma], _name='stosc_d')
        k_period_sma.genData(dataset, gen_new_values=gen_new_values, value='stosc_k')

        
        
