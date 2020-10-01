from v2.strategy.indicators.indicator import Indicator

class SMA(Indicator):
    
    def genData(self, dataset, gen_new_values=True, value='close'):

        period = self.params[0]
        if gen_new_values:
            period.genValue()
        
        dataset[self.name] = dataset[value].rolling(int(period.value)).mean()