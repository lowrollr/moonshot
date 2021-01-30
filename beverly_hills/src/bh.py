import time 
import json

from client import startClient, readData
from data_engine import DataEngine
from server import startServer

class BeverlyHills():
    def __init__(self):
        #initialize all data structures
        self.consumerSocket = None
        self.coins = []
        
        self.consumerConnect()

        self.data_engine = DataEngine(self.coins)

        self.startServer()
        print("Finished set up", flush=True)

    def consumerConnect(self):
        now = time.time()
        timeout = 120 #seconds
        tries = 0
        conn = None

        deadline = now + timeout
        print("Starting Connect")
        while True:
            print("trying to connect", flush=True)
            if time.time() > deadline or conn is not None:
                break
            try:
                conn = startClient()
            except Exception as e:
                tries += 1
                print(e)
                time.sleep(5)
                
        if conn is None:
            raise Exception(f"Was not able to connect with the Data Consumer after {tries} tries. Stop everything")

        print("Connected to Main Data Consumer", flush=True)

        self.consumerSocket = conn
        coins = ""
        while len(coins) == 0:
            print("sending coins", flush=True)
            conn.send(bytes(json.dumps("coins"),encoding='utf-8'))
            coins = readData(conn)
        self.coins = coins

    def startServer(self):
        address_to_function = {"frontend": pingFrontend, "portfolio_manager": self.loop}
        startServer(address_to_function)


    def loop(self):
        #loop for creating data and also sending model prediction to pm
        self.consumerSocket.sendall(json.dumps(bytes("start",encoding='utf-8')))
        #fill up our data
        while not self.data_engine.is_full():
            start = time.time()
            while time.time() < start + 60:
                # coin_data = json.loads(readData())
                pass
            #read from the data_consumer

def pingFrontend(conn):
    while True:
        conn.sendall(json.dumps(bytes(1,encoding='utf-8')))
        time.sleep(2)