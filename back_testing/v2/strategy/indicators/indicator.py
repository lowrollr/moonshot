'''
FILE: indicator.py
AUTHORS:
    -> Jacob Marshall (marshingjay@gmail.com)
WHAT:
    -> This file contains the Indicator superclass
'''

import random

'''
CLASS: Indicator
WHAT:
    -> Indicators implement features that can be calculated with exisitng price data and added to a dataset
'''
class Indicator:

    '''
    ARGS:
        -> _params ([Param]): list of params used for calculations within the Indicator
        -> _appended_name (String) <optional>: string to append to the class name to set as the Indicator name
        -> _name (String) <optional>: name to set as the Indicator name
    RETURN:
        -> None
    WHAT: 
        -> Initializes the indicator name if given, otherwise sets it as the class or subclass name
        -> Sets up the best_values dictionary to store best found values for Indicator params during 
            the execution of a genetic optimization algorithm
    '''
    def __init__(self, _params, _appended_name='', _name=''):
        self.params = _params
        # if a new name is given, set the name as that
        if _name:
            self.name = _name
        else: # otherwise set the name to be this Indicator instance's class name and append the appended_name (if given)
            self.name = self.__class__.__name__ + _appended_name
        self.best_values = {}

    def genData(self, dataset, gen_new_values=True, value='close'):
        # generic indicators don't get added to the dataset as columns because they are simply
        # data used within strategies and thus don't need to be applied to data frames
        if gen_new_values:
            for x in self.params:
                x.genValue()
    
    def shrinkParamRanges(self, percentage):
        if self.best_values:
            for x in self.params:
                x.shrinkRange(self.best_values[x.name], percentage)

    def storeBestValues(self):
        self.best_values = {}
        for x in self.params:
            self.best_values[x.name] = x.value
        return self.best_values