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
        
    def getIndicators(self):
        return self.indicators
    def calc_entry(self, data):
        return 0.0
    def calc_exit(self, data):
        return 0.0
