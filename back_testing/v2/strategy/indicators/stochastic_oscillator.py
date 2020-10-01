from v2.strategy.indicators.indicator import Indicator
from v2.utils import findParams
from v2.utils.strategy.indicators.sma import SMA

class StochasticOscillator(Indicator):
    
    def genData(self, dataset, gen_new_values=True, value='close'):
        param_highlow_range, param_k_period_sma = findParams(self.params, ['highlow_range', 'k_period'])
        highlow_range_value = param_highlow_range.genValue()
        param_k_period_sma.up = highlow_range_value

        dataset['stosc_high_price'] = dataset['low'].rolling(window=highlow_range_value).min()
        dataset['stosc_low_price'] = dataset['high'].rolling(window=highlow_range_value).max()
        dataset['stosc_k'] = 100*((dataset['close'] - dataset['stosc_low_price']) / (dataset['stosc_high_price'] - dataset['stosc_low_price']))

        k_period_sma = SMA([param_k_period_sma], _name='stosc_d')
        k_period_sma.genData(dataset, gen_new_values=False, value='stosc_k')

        
        
