from v2.strategy.indicators.indicator import Indicator
from v2.utils import findParams
from v2.utils.strategy.indicators.sma import SMA

class BollingerBands(Indicator):
    
    def genData(self, dataset, gen_new_values=True, value='close'):
        period = findParams(self.params, ['period'])
        
        boll_sma = SMA([period], _name='boll_sma')
        boll_sma.genData(dataset, value=value)
        dataset['boll_stdev'] = dataset[value].rolling(period.value).std()
        dataset['boll_upper'] = dataset['boll_sma'] + (dataset['boll_stdev'] * 2)
        dataset['boll_lower'] = dataset['boll_sma'] - (dataset['boll_stdev'] * 2)