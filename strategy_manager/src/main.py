import socket
import os
import threading
import sys

class ThreadedServer(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print("Socket Created", flush=True)
        try:
            self.sock.bind((self.host, self.port))
        except Exception as e:
            print(e)
            print("Bind failed. Error : " + str(sys.exc_info()), flush=True)
            sys.exit()

    def listen(self):
        self.sock.listen(5)
        print("Socket now listening", flush=True)
        while True:
            client, address = self.sock.accept()
            print(address, flush=True)
            client.settimeout(60*60)
            threading.Thread(target = self.listenToClient,args = (client,address)).start()

    def listenToClient(self, client, address):
        size = 2048
        while True:
            try:
                data = client.recv(size)
                print(data, flush=True)
                print("yo", flush=True)
                if data:
                    # Set the response to echo back the recieved data 
                    response = data
                    client.send(response)
                else:
                    raise Exception('Client disconnected')
            except:
                client.close()
                return False

if __name__ == "__main__":
    ThreadedServer('127.0.0.1',1234).listen()
