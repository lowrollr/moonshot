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
    def __init__(self, _low = 0.0, _up = 0.0, _prec = 0.0, _name="", _default=0.0):
        self.global_low = _low
        self.global_up = _up
        self.low = _low
        self.up = _up
        self.prec = _prec
        self.value = _default
        self.name = _name
    

    '''
    ARGS:
        -> center (Float): where to center new lower bound and upper bound
        -> shrink_type (String): Which shrinking algo it should use (constrictive, flexible)
        -> percentage (Float): percentage by which to increase lower bound and decrease upper bound
    RETURN:
        -> None
    WHAT: 
        -> Shrinks previous range around a new center value
            hint: just read the code and it will make more sense
        -> Observe that the percentage is equal to half of the overall change in the difference of the upper and lower bounds
    TODO:
        -> make percentage just be the overall delta difference instead of half
    '''
    def shrinkRange(self, center, shrink_type, percentage):
        # compute the current difference between the upper and lower bounds
        delta = self.up - self.low
        # compute and set new bounds
        # note that max() and min() ensure that the delta can not increase by calling this
        
        if shrink_type == "constrictive":
            new_low = max(self.low, center - (percentage * delta))
            new_up = min(self.up, center + (percentage * delta))

            self.low = new_low
            self.up = new_up
        elif shrink_type == "flexible":
            #reading the code below you can see that using zero would not make the parameters shrink (bad)
            if self.global_up == 0.0:
                raise ValueError("For this shrinking algorithm, the max range can not be 0, please use different max value")
            #the global_up should not be zero
            if center - percentage * delta < self.global_low:
                self.low = self.global_low
                self.up = self.global_up * percentage * 2
                self.global_up = self.global_up * percentage * 2
            if center + percentage * delta > self.global_up:
                self.low = self.global_low + self.global_up * ( 1 - percentage * 2)
                self.up = self.global_up
                self.global_low = self.global_low + self.global_up * ( 1 - percentage * 2)
        else:
            raise ValueError("shrink algo is not defined")
        

    '''
    ARGS:
        -> None
    RETURN:
        -> self.value (Float): the new value set for this param
    WHAT: 
        -> Generates a new value within the param's range, w.r.t the param's precision
        -> updates self.value accordingly
    '''
    def genValue(self):
        self.value = round(random.uniform(self.low, self.up), self.prec)
        return self.value