import time 
import json
import socket
import os
from threading import Thread

from client import startClient, readData
from data_engine import DataEngine

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
            conn.send(bytes(json.dumps({"msg":"coins", "destination":"beverly_hills"}),encoding='utf-8'))
            coins = readData(conn)
        print("Received coins from data coinsumer")
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
        s.listen(2)

        while True:
            if self.numClients < 2:
                client, address = s.accept()

                mesg = client.recv(1024)
                mesg_obj = json.loads(mesg)
                if not "msg" in mesg_obj:
                    raise Exception("Did not provide start message in proper format. Need msg as key in dict")
                if mesg_obj["msg"] == "start":
                    if not "destination" in mesg_obj:
                        raise Exception("Did not provide start message in proper format. Need destination as key in dict")
                    if not mesg_obj["destination"] in clientFunctions:
                        raise Exception(f"The provided destination is not in the dictionary. Provided {mesg_obj['destination']}.")
                    
                    self.numClients += 1
                    Thread(target=clientFunctions[mesg_obj["destination"]], args=(client)).start()
            else:
                break
        s.close()

        #send start to data consumer
        self.consumerSocket.sendall(json.dumps(bytes({"msg":"start", "destination":"beverly_hills"},encoding='utf-8')))

def pingFrontend(conn):
    while True:
        conn.sendall(json.dumps(bytes(1,encoding='utf-8')))
        time.sleep(2)