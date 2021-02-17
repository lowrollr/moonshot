import time 
import json
import socket
import os
from threading import Thread
import asyncio
from autobahn.asyncio.websocket import WebSocketServerFactory
from server import BeverlyWebSocketProtocol

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

    def consumerConnect(self):
        conn = None
        print("Starting Connect")
        while True:
            print("Trying to connect", flush=True)
            try:
                conn = client_file.startClient()
                break
            except Exception as e:
                print(e)
                time.sleep(5)

        self.consumerSocket = conn
        coins = ""
        while True:
            #change this to something else 
            rawMsg = {'type': 'coins', 'msg':'', 'src':containersToId['beverly_hills'], 'dest':containersToId['main_data_consumer']}
            conn.send(json.dumps(rawMsg).encode('utf-8'))
            coins = client_file.readData(conn)
            if len(coins) > 0:
                break
            if coins["type"] == "coins":
                coins = json.loads(coins["msg"])
            else:
                raise Exception("Not sending coins back when it should")
        print("Received coins from data consumer")
        coin_msg = json.loads(coins)
        self.coins = coin_msg["msg"]
    
    def compute(self):
        while True:
            time.sleep(2)

    def startServer(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        socketServer = WebSocketServerFactory()
        socketServer.protocol = BeverlyWebSocketProtocol
        
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

    # def acceptConnections(self, clientFunctions):
    #     HOST, PORT = "0.0.0.0", int(os.environ["SERVERPORT"])
    #     s = socket.socket()
    #     try:
    #         s.bind((HOST, PORT))
    #     except socket.error as e:
    #         raise Exception(f"Was not able to create socket server and bind to host and port. Error: {e}")

    #     print("Waiting for a connection")
    #     s.listen(256)

    #     while True:
    #         if self.numClients < 2:
    #             client, address = s.accept()
    #             data = client_file.readDataServer(client)
    #             if data == "":
    #                 continue
    #             if "Sec-WebSocket-Key" in data:
    #                 key = (re.search('Sec-WebSocket-Key:\s+(.*?)[\n\r]+', data)
    #                 .groups()[0]
    #                 .strip())
    #                 response_key = accept(key)
    #                 response = '\r\n'.join(websocket_answer).format(key=response_key)
    #                 client.sendall(response.encode('utf-8'))
    #             data = client_file.readDataServer(client)
    #             print(data)
    #             if not "msg" in mesg_obj:
    #                 raise Exception(f"Did not provide init message in proper format. Need msg as key in dict. Object Received: {mesg_obj}")
    #             if not "type" in mesg_obj:
    #                 raise Exception(f"Did not prvide init message in proper format. Need type as a key in dict. Object Received: {message}")
    #             if not "src" in mesg_obj:
    #                 raise Exception("Did not provide init message in proper format. Need src as key in dict")
    #             if not mesg_obj["src"] in idToContainer:
    #                 raise Exception(f"The provided destination is not in the dictionary. Provided {mesg_obj['src']} from {mesg_obj}.")
    #             print(f"Received connection from {address} or {mesg_obj['src']}")
    #             self.numClients += 1

    #                 # Thread(target=clientFunctions[mesg_obj["source"]], args=(client)).start()
    #         else:
    #             break
    #     s.close()

    #     #send start to data consumer
    #     rawMessage = {'msg':'', 'src':containersToId['beverly_hills'], 'dest':containersToId['main_data_consumer']}
    #     bytesMessage = client_file.constructMsg(json.dumps(rawMessage), "start")
    #     self.consumerSocket.sendall(bytesMessage)
    #     print("Sent start message to main_data_consumer")
    #     while True:
    #         time.sleep(2)

def pingFrontend(conn):
    while True:
        conn.sendall(bytes(1,encoding='utf-8'))
        time.sleep(2)