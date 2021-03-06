import time 
import json
import socket
import os
import zlib 
import zlib
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
        self.previous_data = {}
        self.connections = dict()
        self.numClients = 0
        self.candles = dict()
        self.consumerConnect()
        self.computeEngine = ComputeEngine(coins=self.coins)
        self.loadPrevData()
        

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
        print('Requesting coins and previous data...')
        coins = ""
        while True:
            #change this to something else 
            rawMsg = {'type': 'data', 'msg':'15000', 'src':containersToId['beverly_hills'], 'dest':containersToId['main_data_consumer']}
            conn.send(json.dumps(rawMsg).encode('utf-8'))
            coins = json.loads(readData(conn, 'main_data_consumer', os.environ["DATAPORT"]))
            coin_labels = []
            if coins["type"] == "coins":
                coin_labels = coins['msg']
                break
            elif coins['type'] == "all_data":
                self.previous_data = coins["msg"]
                coin_labels = list(self.previous_data.keys())
                # print(coin_labels)
                print(self.previous_data)
                break
            else:
                raise Exception(f"Not sending coins back when it should. Type sent: {coins['type']} ")

        print("Received coins from data consumer")
        self.coins = coin_labels

    def loadPrevData(self):
        if self.previous_data != {}:
            self.computeEngine.allDataPrepare(self.previous_data)
        
        print('sending start message')
        rawMsg = {'type': 'start', 'msg':'', 'src':containersToId['beverly_hills'], 'dest':containersToId['main_data_consumer']}
        self.connections['main_data_consumer'].send(json.dumps(rawMsg).encode('utf-8'))

    
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



