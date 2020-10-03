from v2.strategy.indicators.indicator import Indicator
from v2.strategy.indicators.ema import EMA
from v2.utils import findParams


class MACD(Indicator):
    

    def genData(self, dataset, gen_new_values=True, value='close'):
        

        #params named 'ema_slow', 'ema_fast', and 'signal' must all be present
        ema_slow_param, ema_fast_param, signal_param = findParams(self.params, ['ema_slow', 'ema_fast', 'signal'])
        if gen_new_values:
            ema_slow_value = ema_slow_param.genValue()
            ema_fast_param.up = ema_slow_value
            ema_fast_value = ema_fast_param.genValue()
            signal_param.up = ema_slow_value
            signal_param.low = ema_fast_value
            signal_param.genValue()

        # generate signal dataset (ema)
        ema_slow = EMA([ema_slow_param], _name='ema_slow')
        ema_slow.genData(dataset, gen_new_values=False, value=value)
        
        ema_fast = EMA([ema_fast_param], _name='ema_fast')
        ema_fast.genData(dataset, gen_new_values=False, value=value)


        dataset[self.name] = dataset['ema_fast'] - dataset['ema_slow']

        signal = EMA([signal_param], _name='signal')
        signal.genData(dataset, gen_new_values=False, value=self.name)
        dataset['macd_diff'] = dataset['macd'] - dataset['signal']