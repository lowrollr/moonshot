from v2.strategy.indicators.indicator import Indicator
from pyti.smoothed_moving_average import smoothed_moving_average as smma

class SMMA(Indicator):
    
    def genData(self, dataset, gen_new_values=True):
        #assumes that the first param is the sma period
        #some indicators require that param names are ascribed correctly
        period = self.params[0]
        if gen_new_values:
            period.genValue()
        
        new_smma = smma(dataset['close'].tolist(), int(period.value))
        
        dataset[self.name] = new_smma