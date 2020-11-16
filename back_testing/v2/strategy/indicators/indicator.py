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


    '''
    ARGS:
        -> dataset (DataFrame): dataset to add the indicator values as a column to
        -> gen_new_values (Boolean) <optional>: weather or not we should generate new values for each param belonging
            to this Indicator
        -> value (String) <optional>: dataframe column name to use for calculations
    RETURN:
        -> None
    WHAT: 
        -> The default implementation doesn't actually do anything with the dataset, but subclass implementations should/do
        -> The default implementation is used to store and vary a value used within a strategy that does not need to be added
            to the dataset or have an abstracted implementation
        -> Here, instead of adding a column to the dataframe, we simply generate new values for each param if necessary
    '''
    def genData(self, dataset, gen_new_values=True, value='close'):
        # generic indicators don't get added to the dataset as columns because they are simply
        # data used within strategies and thus don't need to be applied to data frames
        if gen_new_values: # if we are generating new values, call genValue for each param belonging to this indciator
            for x in self.params:
                x.genValue()

    '''
    ARGS:
        -> percentage (Float): percentage to shrink each bound by for a Param range
    RETURN:
        -> None
    WHAT: 
        -> Shrinks each Param around the current best value by a given percentage on each side (upper and lower)
    '''
    def shrinkParamRanges(self, percentage):
        # this should only be happening if this indicator is part of a genetic algorithm optimization
        if self.best_values:
            for x in self.params:
                x.shrinkRange(self.best_values[x.name], percentage)

    def storeBestValues(self):
        self.best_values = {}
        for x in self.params:
            self.best_values[x.name] = x.value
        return self.best_values