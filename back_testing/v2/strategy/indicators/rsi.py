from v2.strategy.indicators.indicator import Indicator
from v2.utils import findParams
from v2.utils.strategy.indicators.smma import SMMA
import pandas

class RSI(Indicator):
    
    def genData(self, dataset, gen_new_values=True, value='close'):
        period = findParams(self.params, ['period'])
        period.genValue()

        dataset['rsi_diff'] =  dataset[value].diff()

        dataset['rsi_u'] = (abs(dataset['rsi_diff']) + dataset['rsi_diff']) / 2
        dataset['rsi_d'] = (abs(dataset['rsi_diff']) - dataset['rsi_diff']) / 2
        smma_u = SMMA([period], _name='rsi_smma_u')
        smma_d = SMMA([period], _name='rsi_smma_d')
        smma_u.genData(dataset, gen_new_values=False, value='rsi_u')
        smma_d.genData(dataset, gen_new_values=False, value='rsi_d')

        dataset['rsi'] = 100 - (100 / (1 + (dataset['smma_u'] / dataset['smma_d'])))
        