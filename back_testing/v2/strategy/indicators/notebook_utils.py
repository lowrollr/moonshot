'''
FILE: notebook_utils.py
AUTHORS:
    -> Jacob Marshall (marshingjay@gmail.com) 
WHAT:
    -> This file contains utility functions associated with the fetching 
        and manipulation of indicators for research notebooks
    -> Backtesting code should avoid calling these if possible
'''

'''
ARGS:
    -> dataset (DataFrame): dataset to add the indicator values as a column to
    -> gen_new_values (Boolean) <optional>: weather or not we should generate new values for each param belonging
        to this Indicator
    -> value (String) <optional>: dataframe column name to use for calculations
RETURN:
    -> None
WHAT: 
    -> Adds columns with optimal buy/sell
'''
def fetchIndicators(indicator_list):
    indicator_objects = []
    for indicator in indicator_list:



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