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
        
    startBytes = bytes(str(tMsg).rjust(3, 0))
    midBytes = bytes(str(tMsg).rjust(10, 0))
    return startBytes + midBytes + bytes(rawMsg, encoding="utf-8")

def readData(conn):
    data = ''
    while True:
        try:
            buffer = conn.recv(2048)
            if buffer:
                data += buffer.decode('utf-8')
                if len(buffer) < 2048:
                    break
            else:
                break
        except ConnectionResetError as err:
            conn = startClient()
            continue
    try:
        data = json.loads(data)
    except:
        pass
    return data