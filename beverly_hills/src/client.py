import socket
import os
import json
import time
import asyncio
import websocket
from websocket import create_connection

# websocket.enableTrace(True)

def startClient(name, port):
    uri = "ws://" + name + ":" + port
    while True:
        try:
            ws = create_connection(uri)
            if not ws is None:
                print(f"Connected to {name}:{port}\n")
                return ws
            else:
                print(f"Could not connect to {name}:{port}. Retrying...")
        except Exception as e:
            print(f"Could not connect to {name}:{port} because {e}. Retrying...")
        finally:
            time.sleep(3)
    raise Exception(f"Was not able to connect to {name}:{port}")

def readData(conn, name, port):
    while True:
        try:
            data = conn.recv()
            return data
            
        except ConnectionResetError:
            conn = startClient(name, port)
            continue
