import socket
import os
import json
import time

def startClient():
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.connect(("main_data_consumer", int(os.environ["DATAPORT"])))
    return conn

def readData(conn):
    data = ''
    while True:
        buffer = conn.recv(1024)
        if buffer:
            data += buffer.decode('utf-8')
            if len(buffer) < 1024:
                break
        else:
            break
    try:
        data = json.loads(data)
    except:
        pass
    return data