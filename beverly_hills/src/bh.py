'''
FILE: bh.py
AUTHORS:
    -> Jacob Marshall (marshingjay@gmail.com)
    -> Ross Copeland (rhcopeland101@gmail.com)
WHAT:
    -> This file contains core functionality for BH and spins off its various components
        -> starts server and compute engine threads
        -> intializes connections to other containers
        -> request necessary intialization data
'''

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

'''
CLASS: BeverlyHills
WHAT:
    -> Core object that holds everything to do with Beverly Hills, including...
        -> connections to other containers
        -> coins BH will operate on
        -> the compute engine
'''
class BeverlyHills():

    '''
    ARGS:
        -> None
    RETURN:
        -> None
    WHAT: 
        -> Initializes Beverly Hills core object and class variables
    '''
    def __init__(self):
        
        self.coins = [] # list of coins that beverly hills will manage indicators and predictions for
        self.previous_data = {} # stores data retrieved from database (sent from DC)
        self.connections = dict() # maps container names to websocket connections
        self.numClients = 0 # tracks how many clients are connected
        self.candles = dict() # stores most recently received candle objects (from DC), maps coin -> candle

        # connect to DC
        self.consumerConnect() 

        # intialize the Compute Engine
        self.computeEngine = ComputeEngine(coins=self.coins)

        # get any previous data that we have on record
        self.loadPrevData()
        
    '''
    ARGS:
        -> None
    RETURN:
        -> None
    WHAT: 
        -> intitializes the web socket connection to the Data Consumer container
        -> sends initialization messages to request any previous candlestick data available
            in order to initialize data queues for compute engine indicators
    '''
    def consumerConnect(self):
        conn = None

        # start the data consumer client
        print("Connecting to Data Consumer")

        # try to connect every 5 seconds
        while True:
            print("Trying to connect", flush=True)
            try:
                conn = startClient('main_data_consumer', os.environ["DATAPORT"])
                break
            except Exception as e:
                print(e)
                time.sleep(5)

        # store the connection
        self.connections['main_data_consumer'] = conn

        print('Requesting coins and previous data...')
        coins = ""

        # perpetually try to send data requests until a correct response is received
        # should only loop once
        while True:
            # construct the data request message  (requesting 150000 mins of prev data)
            rawMsg = {'type': 'data', 'msg':'15000', 'src':containersToId['beverly_hills'], 'dest':containersToId['main_data_consumer']}

            # send the data request message
            conn.send(json.dumps(rawMsg).encode('utf-8'))

            # load the response
            coins = json.loads(readData(conn, 'main_data_consumer', os.environ["DATAPORT"]))

            # read in the appropriate data according to the type of response receieved
            coin_labels = []
            if coins["type"] == "coins":
                # store the list of coins sent
                coin_labels = coins['msg']
                break
            elif coins['type'] == "all_data":
                # store the candle data received
                self.previous_data = coins["msg"]

                # the coins the DC operating on are each key in the dict of candles 
                coin_labels = list(self.previous_data.keys())
                print(self.previous_data)
                break
            else:
                # raise an exception if an unexpeceted message type was received
                raise Exception(f"Unexpected coin/data request response received: {coins['type']}")

        print("Received coins from data consumer")
        # set coins to the list of coins received
        self.coins = coin_labels


    '''
    ARGS:
        -> None
    RETURN:
        -> None
    WHAT: 
        -> sends retrieved candle data stored in self.previous_data to be processed by the ComputeEngine
        -> sends a start message to DC to let it know that BH is ready to start receiving live data
    '''
    def loadPrevData(self):
        # if previous data is present, send it to the compute engine to fill up indiciator data queues
        if self.previous_data != {}:
            self.computeEngine.allDataPrepare(self.previous_data)
        
        # send the start message to the data consumer
        print('sending start message')
        rawMsg = {'type': 'start', 'msg':'', 'src':containersToId['beverly_hills'], 'dest':containersToId['main_data_consumer']}
        self.connections['main_data_consumer'].send(json.dumps(rawMsg).encode('utf-8'))

    '''
    ARGS:
        -> None
    RETURN:
        -> None
    WHAT: 
        -> reads data from the data consumer websocket and sends it to the Compute Engine to compute indicators
        -> should be called as a function passed to a thread
    '''
    def compute(self):
        # read data forever
        while True:
            # read data from the websocket
            data = json.loads(readData(self.connections["main_data_consumer"], "main_data_consumer", os.environ["DATAPORT"]))

            # send the message content to the compute engine
            self.computeEngine.prepare(data["msg"])
            
    '''
    ARGS:
        -> None
    RETURN:
        -> None
    WHAT: 
        -> creates and starts a socket server to interfact with PM and Frontend
    '''
    def startServer(self):
        # create the server event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # initiate the socket server
        socketServer = WebSocketServerFactory()
        socketServer.protocol = BeverlyWebSocketProtocol

        # make the compute engine a class variable so that the server thread can access it to get predictions
        socketServer.computeEngine = self.computeEngine
        
        # create the  server and bind it to the correct port
        coro = loop.create_server(socketServer, '0.0.0.0', int(os.environ["SERVERPORT"]))

        # start running the server
        server = loop.run_until_complete(coro)
        loop.run_forever()

    '''
    ARGS:
        -> None
    RETURN:
        -> None
    WHAT: 
        -> starts the server thread and compute engine thread
    '''
    def start(self):
        # create server and compute engine thread
        serverThread = Thread(target=self.startServer)
        dataThread = Thread(target=self.compute)

        # start each thread
        serverThread.start()
        dataThread.start()
       


