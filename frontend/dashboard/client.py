import socket
import time
import os
import json
from websocket import create_connection

from vars import (
    containersToId,
    idToContainer
)

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
            print(f"Could not connect to {name}:{port} because {e}. Retrying...", flush=True)
        finally:
            time.sleep(3)
    raise Exception(f"Was not able to connect to {name}:{port}")

def startInit(conn, dest, port):
    while True:
        try:
            rawMessage = {'type':'start', "msg": "", "src":containersToId["frontend"], "dest": containersToId[dest]}
            conn.send(json.dumps(rawMessage).encode('utf-8'))
            return
        except ConnectionResetError:
            conn = startClient(dest, port)

def readData(conn, name, port):
    while True:
        try:
            data = conn.recv()
            return data
            
        except ConnectionResetError:
            conn = startClient(name, port)
            continue

def retrieveCoinData(dc_socket):
    coins = ""
    while True:
        rawMessage = {'type':'coins', 'msg':'', 'src':containersToId["frontend"], 'dest':containersToId['main_data_consumer']}
        dc_socket.send(json.dumps(rawMessage).encode('utf-8'))
        coinMsg = readData(dc_socket, 'main_data_consumer', os.environ['DC_PORT'])
        coins = []
        if "coins" in coinMsg:
            coins = json.loads(coinMsg)["msg"]
        if len(coins) > 0:
            break
    print("Received coins from data consumer")
    return coins

def PMSocket(pm_status, portfolio_datastream, all_positions, coin_positions, current_positions):
    pm_conn = startClient('portfolio_manager', os.environ["PM_PORT"])
    startInit(pm_conn, "portfolio_manager", os.environ["PM_PORT"])
    p_value = 0.0
    
    while True:
        data = readData(pm_conn, 'beverly_hills', os.environ['BH_PORT'])
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
    startInit(bh_conn, "beverly_hills", os.environ["BH_PORT"])
    while True:
        data = readData(bh_conn, 'beverly_hills', os.environ['BH_PORT'])
        if data:
            bh_status.ping()

def DCSocket(dc_conn, dc_status, coin_datastreams):
    while True:
        data, = readData(dc_conn, 'main_data_consumer', os.environ['DC_PORT'])
        data = json.loads(data)
        if data_msg_type == 'curPrice' and data:
            dc_status.ping()
            coin_name = data['msg']['coin'].upper()
            close_price = float(data['msg']['price'])
            for coin in data:
                coin_datastreams[coin_name].update(close_price)

def getCoins():
    dc_conn = startClient('main_data_consumer', os.environ['DC_PORT'])
    coins = retrieveCoinData(dc_conn)
    return dc_conn, coins