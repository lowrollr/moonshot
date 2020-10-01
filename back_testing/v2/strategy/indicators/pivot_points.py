from v2.strategy.indicators.indicator import Indicator
from v2.utils import findParams
from v2.strategy.indicators.sma import SMA
import pandas

class PivotPoints(Indicator):
    def genData(self, dataset, gen_new_values=True, value='close'):
        #ABOUT: https://towardsdatascience.com/pivot-points-calculation-in-python-for-day-trading-659c1e92d323
        period = findParams(self.params, ['period'])[0]
        if gen_new_values:
            period.genValue()
        
        dataset['pp_high'] = dataset[value].rolling(int(period.value)).max()
        dataset['pp_low'] = dataset[value].rolling(int(period.value)).min()
        # this is the close price IRL but that skews the data when we compute on a rolling basis
        # will see how this goes
        pp_sma = SMA([period], _name='pp_sma')
        pp_sma.genData(dataset, gen_new_values=False, value=value)
        dataset['pp_pp'] = (dataset['pp_high'] + dataset['pp_low'] + dataset['pp_sma']) / 3
        dataset['pp_r1'] = (2 * dataset['pp_pp']) - dataset['pp_low']
        dataset['pp_s1'] = (2 * dataset['pp_pp']) - dataset['pp_high']
        dataset['pp_r2'] = dataset['pp_pp'] + (dataset['pp_high'] - dataset['pp_low'])
        dataset['pp_s2'] = dataset['pp_pp'] - (dataset['pp_high'] - dataset['pp_low'])
        dataset['pp_r3'] = dataset['pp_pp'] + (2 * (dataset['pp_high'] - dataset['pp_low']))
        dataset['pp_s3'] = dataset['pp_pp'] - (2 * (dataset['pp_high'] - dataset['pp_low']))
