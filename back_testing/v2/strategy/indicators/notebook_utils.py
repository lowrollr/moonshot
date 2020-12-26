'''
FILE: notebook_utils.py
AUTHORS:
    -> Jacob Marshall (marshingjay@gmail.com) 
WHAT:
    -> This file contains utility functions associated with the fetching 
        and manipulation of indicators for research notebooks
    -> Backtesting code should avoid calling these if possible
'''

from v2.strategy.indicators.param import Param
from v2.strategy.indicators.smma import SMMA
from v2.strategy.indicators.sma import SMA
from v2.strategy.indicators.ema import EMA
from v2.strategy.indicators.wma import WMA
from v2.strategy.indicators.rsi import RSI
from v2.strategy.indicators.bollinger_bands import BollingerBands
from v2.strategy.indicators.stochastic_oscillator import StochasticOscillator
from v2.strategy.indicators.macd import MACD
from v2.strategy.indicators.pivot_points import PivotPoints
from v2.strategy.indicators.variance import Variance
from v2.strategy.indicators.slope import Slope
from v2.strategy.indicators.indicator import Indicator
from v2.strategy.indicators.optimal import Optimal
from v2.strategy.indicators.optimal_v2 import Optimal_v2
from v2.strategy.indicators.ichimoku import Ichimoku
'''
ARGS:
    -> indicator_list ([String]): list of strings that are matched to Indicator objects
    -> param_specification ({String: Value}) <optional>: maps indicator params to values 
RETURN:
    -> None
WHAT: 
    -> initializes each indicator specified in indicator_list (must match strings correctly)
    -> allows for params to be specified in param_specification (again, must match strings correctly)
    -> if a param is not specified in param_specification, a hard-coded default value is used
    -> This is a quality-of-life function for notebooks, should not be used anywhere else
    -> DO NOT CALL THIS FUNCTION UNLESS YOU ARE DOING SO FROM A NOTEBOOK >:(
TODO:
    -> This solution could be much more elegant but works for now
'''
def fetchIndicators(indicator_list, param_specification={}):
    indicator_objects = []

    # find matching indicator for each sting in indicator_list
    # check if param exists in param specification, if so use that value as default param value
    for indicator in indicator_list:
        my_ind = None
        if indicator == 'macd':
            ema_slow_value = 395
            if 'macd.ema_slow' in param_specification:
                ema_slow_value = param_specification['macd.ema_slow']
            macd_ema_slow = Param(5, 10000, 0, 'ema_slow', ema_slow_value)

            ema_fast_value = 285
            if 'macd.ema_fast' in param_specification:
                ema_fast_value = param_specification['macd.ema_fast']
            macd_ema_fast = Param(5, 10000, 0, 'ema_fast', ema_fast_value)

            macd_signal_value = 315
            if 'macd.signal' in param_specification:
                macd_signal_value = param_specification['macd.signal']
            macd_signal = Param(5, 10000, 0, 'signal', macd_signal_value)

            my_ind = MACD(_params=[macd_ema_fast, macd_ema_slow, macd_signal])
        elif indicator == 'ema':
            ema_period_value = 90
            if 'ema.period' in param_specification:
                ema_period_value = param_specification['ema.period']
            ema_period = Param(5, 10000, 0, 'period', ema_period_value)

            my_ind = EMA(_params=[ema_period])
        elif indicator == 'sma':
            sma_period_value = 90
            if 'sma.period' in param_specification:
                sma_period_value = param_specification['sma.period']
            sma_period = Param(5, 10000, 0, 'period', sma_period_value)

            my_ind = SMA(_params=[sma_period])
        elif indicator == 'smma':
            smma_period_value = 90
            if 'smma.period' in param_specification:
                smma_period_value = param_specification['smma.period']
            smma_period = Param(5, 10000, 0, 'period', smma_period_value)

            my_ind = SMMA(_params=[smma_period])
        elif indicator == 'pivot_points':
            pp_period_value = 37
            if 'pivot_points.period' in param_specification:
                pp_period_value = param_specification['pivot_points.period']
            pp_period = Param(5, 10000, 0, 'period', pp_period_value)

            my_ind = PivotPoints(_params=[pp_period])
        elif indicator == 'stochastic_oscillator':
            stoch_highlow_value = 90
            if 'stochastic_oscillator.highlow' in param_specification:
                stoch_highlow_value = param_specification['stochastic_ooscillator.highlow']
            stoch_highlow = Param(5, 10000, 0, 'highlow_range', stoch_highlow_value)

            stoch_k_value = 270
            if 'stochastic_oscillator.k' in param_specification:
                stoch_k_value = param_specification['stochastic_oscillator.k']
            stoch_k = Param(5, 10000, 0, 'k_period', stoch_k_value)

            my_ind = StochasticOscillator(_params=[stoch_highlow, stoch_k])
        elif indicator == 'rsi':
            rsi_period_value = 90
            if 'rsi.period' in param_specification:
                rsi_period_value = param_specification['rsi.period']
            rsi_period = Param(5, 10000, 0, 'period', rsi_period_value)

            my_ind = RSI(_params=[rsi_period])
        elif indicator == 'slope':
            slope_period_value = 60
            if 'slope.period' in param_specification:
                slope_period_value = param_specification['slope.period']
            slope_period = Param(5, 10001, 0, 'period', slope_period_value)

            my_ind = Slope(_params=[slope_period])
        elif indicator == 'variance':
            var_period_value = 90
            if 'variance.period' in param_specification:
                var_period_value = param_specification['variance.period']
            var_period = Param(5, 10000, 0, 'period', var_period_value)

            my_ind = Variance(_params=[var_period])
        elif indicator == 'bollinger_bands':
            boll_period_value = 90
            if 'bollinger_bands.period' in param_specification:
                boll_period_value = param_specification['bollinger_bands.period']
            boll_period = Param(5, 10000, 0, 'period', boll_period_value)

            my_ind = BollingerBands(_params=[boll_period])
        elif indicator == 'optimal':
            optimal_penalty_value = 0.0026
            if 'optimal.penalty' in param_specification:
                optimal_penalty_value = param_specification['optimal.penalty']
            optimal_penalty = Param(0, 0, 0, 'penalty', optimal_penalty_value)

            my_ind = Optimal(_params=[optimal_penalty])
        elif indicator == 'ichimoku':
            short_window_val, medium_window_val, long_window_val = 9, 26, 52
            if 'ichimoku.short_window' in param_specification:
                short_window_val = param_specification['ichimoku.short_window']
            short_window = Param(5, 50, 0, 'short_window', short_window_val)

            if 'ichimoku.medium_window' in param_specification:
                medium_window_val = param_specification['ichimoku.medium_window']
            medium_window = Param(15, 75, 0, 'medium_window', medium_window_val)
            
            if 'ichimoku.long_window' in param_specification:
                long_window_val = param_specification['ichimoku.long_window']
            long_window = Param(40, 200, 0, 'long_window', long_window_val)

            my_ind = Ichimoku(_params=[short_window, medium_window, long_window])
        elif indicator == 'optimal_v2':
            my_ind = Optimal_v2(_params=[])
        elif indicator == "wma":
            wma_period_value = 90
            if 'wma.period' in param_specification:
                wma_period_value = param_specification['wma.period']
            wma_period = Param(5, 10000, 0, 'period', wma_period_value)
            my_ind = WMA(_params=[wma_period])
        else:
            raise Exception('Invalid Indicator Name: ' + str(indicator))

        # append the corresponding indicator to the list of objects that will be returned
        indicator_objects.append(my_ind)
        
    return indicator_objects


'''
ARGS:
    -> dataset (DataFrame): dataset to add indicators to
    -> indicators ([Indicator]): list of indicator objects that need added to the dataset
RETURN:
    -> None
WHAT: 
    -> Generates data for each Indicator and puts it in the dataset
'''
def genDataForAll(dataset, indicators):
    for x in indicators:
        x.genData(dataset, gen_new_values=False)