
from collections import deque
from sys import maxsize

class DataQueue:
    def __init__(self, maxlen=15000):
        self.queue = deque(maxlen=maxlen)
        self.curMin = maxsize()
        self.curMax = -1 * maxsize()
        self.full = False


    def addData(self, dataPt):
        if not self.full and len(self.queue) == self.queue.maxlen:
            self.full = True
        if self.full:
            firstItem = self.queue.popleft()
            
            if firstItem == self.curMin:
                self.curMin = min(self.queue)
            if firstItem == self.curMax:
                self.curMax == max(self.queue)

        self.queue.append(dataPt)
        self.curMax = max(self.curMax, dataPt)
        self.curMin = min(self.curMin, dataPt)