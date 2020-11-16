'''
FILE: load_config.py
AUTHORS:
    -> Jacob Marshall (marshingjay@gmail.com)
WHAT:
    -> This file contains functionality for loading the configuration file
'''

'''
ARGS:
    -> None
RETURN:
    -> my_config ({String: String}): dictionary mapping param names to param values
WHAT: 
    -> Parses input from config file (config.config) and reads it into a dictionary

'''
def load_config():
    my_config = {}
    with open('config.config') as config:
        for line in config:
            args = line.split('=')
            my_config[args[0]] = args[1].rstrip().split(',')
    return my_config