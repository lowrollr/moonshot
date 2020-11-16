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

        
    def process(self, data):
        # this happens every tick
        # use this to keep track of things that need to be kept track of over multiple ticks

        pass
        
    def getIndicators(self):
        return self.indicators
    def calc_entry(self, data):
        return 0.0
    def calc_exit(self, data):
        return 0.0
