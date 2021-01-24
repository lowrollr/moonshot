import socket

def startClient():

    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.connect(("main_data_consumer", 9090))
    print("connected", flush=True)
