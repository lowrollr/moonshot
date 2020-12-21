'''
FILE: load_config.py
AUTHORS:
    -> Jacob Marshall (marshingjay@gmail.com)
WHAT:
    -> This file contains functionality for loading the configuration file
'''
import hjson
'''
ARGS:
    -> None
RETURN:
    -> my_config ({String: String}): dictionary mapping param names to param values
WHAT: 
    -> Parses input from config file (config.config) and reads it into a dictionary
'''
def load_config(config_file):
    with open(config_file) as config:
        return hjson.load(config)