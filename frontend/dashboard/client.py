import socket
import time
import os
import json

def startClient(name, port):
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
            print(f"Could not connect to {name}:{port} because {e}. Retrying...", flush=True)
        finally:
            time.sleep(3)
            
    raise Exception(f"Was not able to connect to {name}:{port}")

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
        if data:
            data = json.loads(data)
        else:
            data = dict()
    except:
        pass
    return data

def retrieveCoinData(dc_socket):
    coins = ""
    # time.sleep(1)
    while True:
        dc_socket.sendall(bytes(json.dumps({"msg":"coins", "source":"frontend", "destination":"main_data_consumer"}),encoding='utf-8'))
        coins = readData(dc_socket)
        if len(coins) > 0:
            break
    print("Received coins from data coinsumer")
    return coins

def PMSocket(pm_status, portfolio_datastream, all_positions, coin_positions, current_positions):
    pm_conn = startClient('portfolio_manager', os.environ["PM_PORT"])
    pm_conn.sendall()
    p_value = 0.0
    
    while True:
        data = readData(pm_conn)
        if data:
            pm_status.ping()
            if 'enter' in data:
                coin, amnt, price, allocation = data['enter']
                current_positions.openPosition(coin, amnt, price, allocation, p_value)

            elif 'exit' in data:
                coin, amnt, price = data['exit']
                closed_position = current_positions.closePosition(coin, amnt, price)
                if closed_position:
                    all_positions.append(closed_position)
                    coin_positions[coin].append(closed_position)
            elif 'portfolio_value' in data:
                p_value = data['portfolio_value']
                portfolio_datastream.update(p_value)


def BHSocket(bh_status):
    bh_conn = startClient('beverly_hills', os.environ['BH_PORT'])
    while True:
        data = readData(bh_conn)
        if data:
            bh_status.ping()

def DCSocket(dc_conn, dc_status, coin_datastreams):
    
    while True:
        data = readData(dc_conn)
        if data:
            dc_status.ping()
            for coin in data:
                coin_datastreams[coin].update(data[coin])

def getCoins():
    dc_conn = startClient('main_data_consumer', os.environ['DC_PORT'])
    coins = retrieveCoinData(dc_conn)

    return dc_conn, coins