import socket
import os
import threading
import sys
import time
from bh import BeverlyHills

if __name__ == "__main__":
    time.sleep(8)
    beverly = BeverlyHills()

    beverly.loop()