import socket
import os
from threading import Thread

def threaded_client(connection, addr, protocol_action):
    
    if addr not in protocol_action:
        raise Exception(f"There was addr not associated with a function. Addr {addr}")
    else:
        protocol_action[addr](connection)
        
    connection.close()

def startServer(protocol_function):
    HOST, PORT = "0.0.0.0", os.environ["SERVERPORT"]
    s = socket.socket()
    try:
        s.bind((HOST, PORT))
    except socket.error as e:
        raise Exception(f"Was not able to create socket server and bind to host and port. Error: {e}")

    print("Waiting for a connection")
    s.listen(2)

    while True:
        client, address = s.accept()
        Thread(target=threaded_client, args=(client, address, protocol_function)).start()

    s.close()