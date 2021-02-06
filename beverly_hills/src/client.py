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

def readData(conn):
    data = ''
    while True:
        try:
            buffer = conn.recv(1024)
            if buffer:
                data += buffer.decode('utf-8')
                if len(buffer) < 1024:
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