import socket
import time
import os
import json

def startClient(name, port):
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.connect((name, port))
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
        if data:
            data = json.loads(data)
        else:
            data = dict()
    except:
        pass
    return data

def PMSocket(connect_url, pm_status, portfolio_datastream, all_positions, coin_positions, current_positions):
    pm_conn = startClient('portfolio_manager', os.environ["PM_PORT"])
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


def BHSocket(connect_url, bh_status):
    bh_conn = startClient('beverly_hills', os.environ['BH_PORT'])
    while True:
        data = readData(bh_conn)
        if data:
            bh_status.ping()



def DCSocket(connect_url, dc_status, coin_datastreams):
    dc_conn = startClient('data_consumer', os.environ['DC_PORT'])
    while True:
        data = readData(dc_conn)
        if data:
            dc_status.ping()
            for coin in data:
                coin_datastreams[coin].update(data[coin])