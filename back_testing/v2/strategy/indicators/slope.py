from v2.strategy.indicators.indicator import Indicator
from v2.utils import findParams
import pandas

class Slope(Indicator):
    def genData(self, dataset, gen_new_values=True, value='close'):
        period = findParams(self.params, ['period'])[0]
        if gen_new_values:
            period.genValue()

        dataset['slope'] = (dataset[value].rolling(window=int(period.value)).max() - dataset[value].rolling(window=int(period.value)).min()) / dataset[value].rolling(window=int(period.value)).max()