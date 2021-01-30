import socket
import os
import threading
import sys
import time
from bh import BeverlyHills
from data_engine import DataEngine
from server import startServer
from client import startClient

if __name__ == "__main__":
    beverly = BeverlyHills()

    beverly.loop()