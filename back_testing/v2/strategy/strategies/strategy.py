'''
FILE: strategy.py
AUTHORS:
    -> Jacob Marshall (marshingjay@gmail.com)
WHAT:
    -> This file contains the Strategy superclass
'''

'''
CLASS: Strategy
WHAT:
    -> Implements a given order execution strategy
TODO:
    -> Maybe entry/exit functions should return Floats corresponding to confidence? (How would this impact the rest of our 
        infrastructure?)
'''
class Strategy:

    '''
    ARGS:
        -> None
    RETURN:
        -> None
    WHAT: 
        -> default __init__ implementation
        -> Nothing to see here, every subclass will have its own implementation of this
        -> Each subclass should instantiate and populate its list of Indicators so that they may be added to the dataset
            before the strategy is executed
    '''
    def __init__(self):
        self.indicators = []
        self.is_ml = False

    '''
    ARGS:
        -> data (Tuple): a single row from a dataframe
    RETURN:
        -> None
    WHAT: 
        -> this will be called every tick by the backtesting model
        -> put things in here that you want to happen every tick
            or want to keep track of between ticks
    '''
    def process(self, data):
        pass


    '''
    ARGS:
        -> None
    RETURN:
        -> self.indicators ([Indicator]): Strategy object's list of Indicator objects
    WHAT: 
        -> returns the Strategy's list of indicators
    '''
    def getIndicators(self):
        return self.indicators


    '''
    ARGS:
        -> data (Tuple): a single row from a dataframe
    RETURN:
        -> (Boolean): Whether or not to enter a position
    WHAT: 
        -> given the current data row, determine whether or not to enter a position
    '''  
    def calc_entry(self, data):
        return False


    '''
    ARGS:
        -> data (Tuple): a single row from a dataframe
    RETURN:
        -> (Boolean): Whether or not to exit a position
    WHAT: 
        -> given the current data row, determine whether or not to exit a position
    '''  
    def calc_exit(self, data):
        return False
