from v2.strategy.indicators.indicator import Indicator
from v2.utils import findParams
import pandas
import numpy as np

class Variance(Indicator):
    def process_variance(self, var_std, var_mean, cur_var):
        if cur_var > var_mean + (2 * var_std):
            return 0.5
        elif cur_var < max(0, var_mean - (2 * var_std)):
            return 0.1
        else:
            span = (var_mean + (2 * var_std)) - (var_mean - (2 * var_std))
            unscaled_coeff = float(cur_var - (var_mean - (2 * var_std))) / float(span)

            return 0.1 + (unscaled_coeff * 0.4)


    def genData(self, dataset, gen_new_values=True, value='close'):
        period = findParams(self.params, ['period'])[0]
        if gen_new_values:
            period.genValue()
        



        dataset['variance'] = dataset[value].rolling(window=int(period.value)).var()

        stop_loss_percentage = findParams(self.params, ['stop_loss_percentage'])[0]
        if stop_loss_percentage:
            var_std = np.std(dataset['variance'])
            avg_var = np.mean(dataset['variance'])
            dataset['stop_loss_percentage'] = dataset.apply(lambda x: self.process_variance(var_std, avg_var, x.variance), axis=1)
