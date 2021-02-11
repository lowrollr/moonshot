import socket
import os
import json
import time

def startClient():
    name = "main_data_consumer"
    port = os.environ["DATAPORT"]
    while True:
        try:
            conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            conn.connect((name, int(port)))
            if not conn is None:
                print(f"Connected to {name}:{port}\n")
                return conn
            else:
                print(f"Could not connect to {name}:{port}. Retrying...")
        except Exception as e:
            print(f"Could not connect to {name}:{port} because {e}. Retrying...")
        finally:
            time.sleep(3)
    raise Exception(f"Was not able to connect to {name}:{port}")

def constructMsg(rawMsg, msgType):
    tMsg = 0
    if msgType == "ping":
        tMsg = 1
    elif msgType == "coinRequest":
        tMsg = 2
    elif msgType == "coinServe":
        tMsg = 3
    elif msgType == "init":
        tMsg = 4
    elif msgType == "start":
        tMsg = 5
    elif msgType == "curPrice":
        tMsg = 6
    elif msgType == "candleStick":
        tMsg = 7
    else:
        raise ValueError(f"The message type is not defined: {msgType}")
        
    startBytes = bytes(str(tMsg).rjust(3, '0'), encoding='utf-8')
    midBytes = bytes(str(tMsg).rjust(10, '0'), encoding='utf-8')
    return startBytes + midBytes + bytes(rawMsg, encoding="utf-8")

def parseMsgType(byteType):
    numType = int(byteType)
    if numType == 1:
        return "ping"
    elif numType == 2:
        return "coinRequest"
    elif numType == 3:
        return "coinServe"
    elif numType == 4:
        return "init"
    elif numType == 5:
        return "start"
    elif numType == 6:
        return "curPrice"
    elif numType == 7:
        return "candleStick"
    else:
        raise ValueError("Num type is not defined: " + str(numType))

def readData(conn):
    while True:
        try:
            msgType = conn.recv(3)
            #do stuff with message type
            msgLen = int(conn.recv(10))

            #should change this because this could be ridiculous number
            # making it really slow
            data = conn.recv(msgLen)

            return data, parseMsgType(msgType)
            
        except ConnectionResetError:
            conn = startClient()
            continue