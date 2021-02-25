import time 
import json
import socket
import os
from threading import Thread, Lock
import asyncio
from autobahn.asyncio.websocket import WebSocketServerFactory
from server import BeverlyWebSocketProtocol

from client import (
    startClient,
    readData
)
from compute import ComputeEngine
from vars import (
    containersToId,
    idToContainer
)



class BeverlyHills():
    def __init__(self):
        #initialize all data structures
        self.coins = []
        self.connections = dict()
        self.numClients = 0
        self.candles = dict()
        self.consumerConnect()
        self.computeEngine = ComputeEngine(coins=self.coins)
        

    def consumerConnect(self):
        conn = None
        print("Connecting to Data Consumer")
        while True:
            print("Trying to connect", flush=True)
            try:
                conn = startClient('main_data_consumer', os.environ["DATAPORT"])
                break
            except Exception as e:
                print(e)
                time.sleep(5)

        self.connections['main_data_consumer'] = conn
        print('requesting coins')
        coins = ""
        while True:
            #change this to something else 
            rawMsg = {'type': 'coins', 'msg':'', 'src':containersToId['beverly_hills'], 'dest':containersToId['main_data_consumer']}
            conn.send(json.dumps(rawMsg).encode('utf-8'))
            coins = readData(conn, 'main_data_consumer', os.environ["DATAPORT"])
            if len(coins) > 0:
                break
            if coins["type"] == "coins":
                coins = json.loads(coins["msg"])
            else:
                raise Exception("Not sending coins back when it should")
        print("Received coins from data consumer")
        coin_msg = json.loads(coins)
        self.coins = coin_msg["msg"]

        print('sending start message')
        rawMsg = {'type': 'start', 'msg':'', 'src':containersToId['beverly_hills'], 'dest':containersToId['main_data_consumer']}
        conn.send(json.dumps(rawMsg).encode('utf-8'))

    
    def compute(self):
        while True:
            data = json.loads(readData(self.connections["main_data_consumer"], "main_data_consumer", os.environ["DATAPORT"]))
            
            self.computeEngine.prepare(data["msg"])
            
            

    def startServer(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        socketServer = WebSocketServerFactory()
        socketServer.protocol = BeverlyWebSocketProtocol
        socketServer.computeEngine = self.computeEngine
        
        coro = loop.create_server(socketServer, '0.0.0.0', int(os.environ["SERVERPORT"]))
        server = loop.run_until_complete(coro)
        loop.run_forever()

    def loop(self):
        #split off two threads, one for starting server and handling connections.
        #   wait on data from dc and compute
        serverThread = Thread(target=self.startServer)
        dataThread = Thread(target=self.compute)

        serverThread.start()
        dataThread.start()
       

    def initFrontEndConnection(self):
        print("Connecting to Frontend")
        while True:
            print("Trying to connect", flush=True)
            try:
                conn = startClient('frontend', os.environ["DATAPORT"])
                break
            except Exception as e:
                print(e)
                time.sleep(5)



