from v2.strategy.indicators.indicator import Indicator
from v2.strategy.indicators.ema import EMA

from pyti.moving_average_convergence_divergence import moving_average_convergence_divergence as macd

class MACD(Indicator):
    

    def genData(self, dataset, gen_new_values):
        # due to the nature of macd we will always generate new values
        # if this causes a problem we can change it 

        #params named 'ema_slow', 'ema_fast', and 'signal' must all be present
        ema_slow_param = next((x for x in self.params if x.name == 'ema_slow'), None)
        ema_fast_param = next((x for x in self.params if x.name == 'ema_fast'), None)
        signal_param = next((x for x in self.params if x.name == 'signal'), None)
        #make sure that fast >= signal >= slow
        ema_slow_value = ema_slow_param.genValue()
        ema_fast_param.up = ema_slow_value
        ema_fast_value = ema_fast_param.genValue()
        signal_param.up = ema_slow_value
        signal_param.low = ema_fast_value
        signal_param.genValue()

        # generate signal dataset (ema)
        signal = EMA([signal_param], _name='signal')
        signal.genData(dataset, gen_new_value=False)

        dataset[self.name] = macd(dataset, ema_fast_value, ema_slow_value)