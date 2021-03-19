'''
FILE: vars.py
AUTHORS:
    -> Ross Copeland (rhcopeland101@gmail.com)
WHAT:
    -> holds vars mapping containers to id and vice versa
'''

# map container names to internal ids
containersToId = {
    "main_data_consumer":0,
    "beverly_hills":1,
    "portfolio_manager":2,
    "frontend":3
}

# map internal ids to container names
idToContainer = {
    0:"main_data_consumer",
    1:"beverly_hills",
    2:"portfolio_manager",
    3:"frontend"
}