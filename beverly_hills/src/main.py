'''
FILE: main.py
AUTHORS:
    -> Jacob Marshall (marshingjay@gmail.com)
WHAT:
    -> Starts Beverly Hills
        -> manages ML models and their inputs
        -> feeds predictions to PM when requeusted
'''

from bh import BeverlyHills

if __name__ == "__main__":
    # initialize Beverly Hills
    beverly = BeverlyHills()

    # starts compute engine and server thread
    beverly.start()