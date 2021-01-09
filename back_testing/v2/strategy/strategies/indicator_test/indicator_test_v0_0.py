'''
FILE: indicator_test_v0_0.py
AUTHORS:
    -> Jacob Marshall (marshingjay@gmail.com)
WHAT:
    -> This file is used for the testing and debugging of indicators
'''
from v2.strategy.strategies.strategy import Strategy

'''
CLASS: indicator_test
WHAT:
    -> Creates a strategy class that can be specified within the config
    -> This is used so that you can use debugger
    -> Params Required:
        -> None
'''

class indicator_test(Strategy):
    '''
    ARGS:
        -> None
    RETURN:
        -> None
    WHAT: 
        -> calculates and adds the indicators to self.indicators to be tested
    '''
    def __init__(self, entry_models=[], exit_models=[]):
        super().__init__(entry_models, exit_models)
        # wanna test some indicators?
        # do that here 
        self.indicators.extend([])
        
