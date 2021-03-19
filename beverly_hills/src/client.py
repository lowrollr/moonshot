'''
FILE: client.py
AUTHORS:
    -> Jacob Marshall (marshingjay@gmail.com)
    -> Ross Copeland (rhcopeland101@gmail.com)
WHAT:
    -> This file contains implementation of the BH client, which pings back and forth with frontend and that's all right now
'''

import socket
import os
import json
import time
import asyncio
from websocket import create_connection

'''
ARGS:
    -> name (String): name of container to connect to
    -> port (String): port of container to connect to
RETURN:
    -> ws (WebsocketConnection): websocket connection to the passed in container 
WHAT: 
    -> Initializes a websocket connection 
'''
def startClient(name, port):

    # construct the address
    uri = "ws://" + name + ":" + port

    # try to connect indefinitely
    while True:
        try:
            # create the connection to the given address
            ws = create_connection(uri)
            if not ws is None:
                print(f"Connected to {name}:{port}\n")
                # return the connection if it was created succesfully
                return ws
            else:
                print(f"Could not connect to {name}:{port}. Retrying...")
        except Exception as e:
            print(f"Could not connect to {name}:{port} because {e}. Retrying...")
        finally:
            time.sleep(3)
    raise Exception(f"Was not able to connect to {name}:{port}")

'''
ARGS:
    -> conn (WebsocketConnection): websocket to read data from 
    -> name (String): name of container that connection belongs to
    -> port (String): port connection is on
RETURN:
    -> data ({string: string}): data
WHAT:
    -> Reads data from the websocket
    -> If the connection is dropped, restart the client
'''
def readData(conn, name, port):
    # try to read from the socket indefinitely
    while True:
        try:
            data = conn.recv()
            return data
            
        except ConnectionResetError:
            conn = startClient(name, port)
            continue