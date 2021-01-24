import socket
import os
from threading import Thread

def threaded_client(connection):
    connection.send(str.encode('Welcome to the Server\n'))
    print("finished sending")
    while True:
        data = connection.recv(2048)
        reply = 'Server Says: ' + data.decode('utf-8')
        if not data:
            break
        print(data)
        connection.sendall(str.encode(reply))
    connection.close()

def startServer():
    HOST, PORT = "0.0.0.0", 1234
    ThreadCount = 0
    s = socket.socket()
    try:
        s.bind((HOST, PORT))
    except socket.error as e:
        print(str(e))

    print("Waiting for a connection")
    s.listen(2)

    while True:
        Client, address = s.accept()
        print('Connected to: ' + address[0] + ':' + str(address[1]))
        Thread(target=threaded_client, args=(Client, )).start()
        ThreadCount += 1
        print('Thread Number: ' + str(ThreadCount))
    s.close()