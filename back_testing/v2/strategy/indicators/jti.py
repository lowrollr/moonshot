'''
FILE: jti.py
AUTHORS:
    -> Jacob Marshall (marshingjay@gmail.com)
WHAT:
    -> This file contains the Jacob Triangulation Indicator
'''

import pandas
import numpy as np

from math import sqrt, acos
from sys import maxsize
from v2.strategy.indicators.param import Param
from v2.strategy.indicators.indicator import Indicator
from v2.utils import findParams
from v2.strategy.indicators.sma import SMA

'''
CLASS: JTI
WHAT:
    -> What is JTI? --> Jacob's Triangulation Indicator
    -> Params Required:
        -> 'period'
    -> this indicator has an unstable period
'''
class JTI(Indicator):

    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: weather or not we should generate new values for each param belonging
            to this Indicator
        -> value (String) <optional>: dataframe column name to use for calculations
    RETURN:
        -> None
    WHAT: 
        -> calculates JTI for the given period
    '''
    def genData(self, dataset, gen_new_values=True):
        period = findParams(self.params, ['period'])[0]
        if gen_new_values:
            period.genValue()
        
        
        dataset[self.name + '_a'] = np.NAN
        dataset[self.name + '_b'] = np.NAN
        dataset[self.name + '_c'] = np.NAN
        dataset[self.name + '_theta'] = np.NAN
        
        curMin = (maxsize, 0)
        curMax = (0, 0)
        lastMin = (maxsize, 0)
        lastMax = (0, 0)
        lookingForMax = True
        for row in dataset.itertuples():
            
            index = row.Index
            cur_value = getattr(row, self.value)
            if lookingForMax:
                
                if curMin[1] and lastMax[1]:
                    minutes_since_max = int((row.time - lastMax[1]) / 60000)
                    minutes_since_min = int((row.time - curMin[1]) / 60000)
                    minutes_between = int((curMin[1] - lastMax[1]) / 60000)
                    jti_a = sqrt(pow(minutes_since_min, 2) + pow((1 - (curMin[0]/row.close)), 2))
                    jti_b = sqrt(pow(minutes_since_max, 2) + pow((1 - (lastMax[0]/row.close)), 2))
                    jti_c = sqrt(pow(minutes_between, 2) + pow((1 - (lastMax[0]/curMin[0])), 2))
                    cos_c = (pow(jti_a, 2) + pow(jti_b, 2) - pow(jti_c, 2)) / (2 * jti_a * jti_b)
                    jti_theta = 0.0
                    try:
                        jti_theta = acos(cos_c)
                    except ValueError as err:
                        jti_theta = 0.0
                    
                    dataset.at[index, self.name + '_a'] = jti_a
                    dataset.at[index, self.name + '_b'] = jti_b
                    dataset.at[index, self.name + '_c'] = jti_c
                    dataset.at[index, self.name + '_theta'] = jti_theta

                if cur_value < curMax[0]:
                    lookingForMax = False
                    lastMin = curMin
                    curMin = (cur_value, row.time)
                else:
                    curMax = (cur_value, row.time)

            else:
                if curMax[1] and lastMin[1]:
                    minutes_since_max = int((row.time - curMax[1]) / 60000)
                    minutes_since_min = int((row.time - lastMin[1]) / 60000)
                    minutes_between = int((curMax[1] - lastMin[1]) / 60000)
                    jti_a = sqrt(pow(minutes_since_max, 2) + pow((1 - (curMax[0]/row.close)), 2))
                    jti_b = sqrt(pow(minutes_since_min, 2) + pow((1 - (lastMin[0]/row.close)), 2))
                    jti_c = sqrt(pow(minutes_between, 2) + pow((1 - (lastMin[0]/curMax[0])), 2))
                    cos_c = (pow(jti_a, 2) + pow(jti_b, 2) - pow(jti_c, 2)) / (2 * jti_a * jti_b)

                    jti_theta = 0.0
                    try:
                        jti_theta = acos(cos_c)
                    except ValueError as err:
                        jti_theta = 0.0
                    
                    dataset.at[index, self.name + '_a'] = jti_a
                    dataset.at[index, self.name + '_b'] = jti_b
                    dataset.at[index, self.name + '_c'] = jti_c
                    dataset.at[index, self.name + '_theta'] = jti_theta
                
                if cur_value > curMin[0]:
                    lookingForMax = True
                    lastMax = curMax
                    curMax = (cur_value, row.time)
                else:
                    curMin = (cur_value, row.time)
            

        return [self.name + '_a',  self.name + '_b', self.name + '_c', self.name + '_theta']

    def setDefaultParams(self):
        self.params = [
            Param(5,10000,0,'period',60)
        ]