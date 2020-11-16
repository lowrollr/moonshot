'''
FILE: param.py
AUTHORS:
    -> Jacob Marshall (marshingjay@gmail.com)
WHAT:
    -> This file contains the Param superclass
'''

import random

'''
CLASS: Param
WHAT:
    -> Params store values that exist as a part of strategies/indicators
    -> These values exist as part of calculations
    -> It's possible we'd want to change/randomize these values over a given range for optimization purposes
    -> This class allows for that functionality
'''
class Param:

    '''
    ARGS:
        -> _low (Float): lower bound of range of values that Param can take on
        -> _high (Float): upper bound of range of values that Param can take on
        -> _prec (Float): precision of value
        -> _default (Float): initial value for this param
        -> _name (String): the name of this param
    RETURN:
        -> None
    WHAT: 
        -> Initializes param value, range, precision, and name
    '''
    def __init__(self, _low, _up, _prec, _name, _default):
        self.low = _low
        self.up = _up
        self.prec = _prec
        self.value = _default
        self.name = _name
    
    def shrinkRange(self, center, percentage):
        delta = self.up - self.low
        new_low = max(self.low, center - (percentage * delta))
        new_up = min(self.up, center + (percentage * delta))
        self.low = new_low
        self.up = new_up

    def genValue(self):
        self.value = round(random.uniform(self.low, self.up), self.prec)
        return self.value