import time 
import json
import socket
import os
from threading import Thread

import client as client_file
from data_engine import DataEngine
from vars import (
    containersToId,
    idToContainer
)
class BeverlyHills():
    def __init__(self):
        #initialize all data structures
        self.consumerSocket = None
        self.coins = []
        self.connections = dict()
        self.numClients = 0
        
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
                conn = client_file.startClient()
            except Exception as e:
                tries += 1
                print(e)
                time.sleep(5)

        self.consumerSocket = conn
        coins = ""
        while True:
            #change this to something else 
            rawMsg = {'msg':'', 'src':containersToId['beverly_hills'], 'dest':containersToId['main_data_consumer']}
            bytesMsg = client_file.constructMsg(json.dumps(rawMsg), "coinRequest")
            conn.sendall(bytes(bytesMsg, encoding='utf-8'))
            coins = client_file.readData(conn)
            if len(coins) > 0:
                break
        print("Received coins from data consumer")
        self.coins = coins

    def startServer(self):
        address_to_function = {"frontend": pingFrontend, "portfolio_manager": self.loop}
        self.acceptConnections(address_to_function)

    def loop(self):
        #loop for creating data and also sending model prediction to pm
        
        #fill up our data
        while not self.data_engine.is_full():
            start = time.time()
            while time.time() < start + 60:
                # coin_data = json.loads(readData())
                pass
            #read from the data_consumer

    def acceptConnections(self, clientFunctions):
        HOST, PORT = "0.0.0.0", int(os.environ["SERVERPORT"])
        s = socket.socket()
        try:
            s.bind((HOST, PORT))
        except socket.error as e:
            raise Exception(f"Was not able to create socket server and bind to host and port. Error: {e}")

        print("Waiting for a connection")
        s.listen(256)

        while True:
            if self.numClients < 2:
                client, address = s.accept()
                data, msgType = client_file.readData(client)
                mesg_obj = json.loads(data)
                
                if not "msg" in mesg_obj:
                    raise Exception(f"Did not provide init message in proper format. Need msg as key in dict. Object Received: {mesg_obj}")
                if msgType == "init":
                    if not "src" in mesg_obj:
                        raise Exception("Did not provide init message in proper format. Need src as key in dict")
                    if not mesg_obj["src"] in clientFunctions:
                        raise Exception(f"The provided destination is not in the dictionary. Provided {mesg_obj['src']} from {mesg_obj}.")
                    print(f"Received connection from {address} or {mesg_obj['src']}")
                    self.numClients += 1

                    # Thread(target=clientFunctions[mesg_obj["source"]], args=(client)).start()
            else:
                break
        s.close()

        #send start to data consumer
        rawMessage = {'msg':'', 'src':containersToId['beverly_hiills'], 'dest':containersToId['main_data_consumer']}
        bytesMessage = client_file.constructMsg(json.dumps(rawMessage), "start")
        self.consumerSocket.sendall(bytes(bytesMessage,encoding='utf-8'))
        while True:
            time.sleep(2)

def pingFrontend(conn):
    while True:
        conn.sendall(bytes(1,encoding='utf-8'))
        time.sleep(2)