"""
FILE: multiprocess.py
AUTHORS:
    -> Ross Copeland (rhcopeland101@gmail.com)
WHAT:
    -> This file contains class for multiprocessing so we use the same pool throughout
"""

import multiprocessing as mp

"""

"""
class Multiprocess():
    def __init__(self, num_processes=-1):
        p = num_processes
        if num_processes == -1:
            p = mp.cpu_count()
        self.pool = mp.Pool(processes=p)

    def getPool(self):
        return self.pool
