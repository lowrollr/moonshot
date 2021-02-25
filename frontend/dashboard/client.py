import socket
import time
import os
import json
from websocket import create_connection

from vars import (
    containersToId,
    idToContainer
)

def startClient(name, port, reconnect=False):
    uri = "ws://" + name + ":" + port
    while True:
        try:
            ws = create_connection(uri)
            if not ws is None:
                print(f"Connected to {name}:{port}\n")
                if reconnect:
                    rawMessage = {'type':'reconnect', 'msg':'', 'src':containersToId["frontend"], 'dest':containersToId[name]}
                    ws.send(json.dumps(rawMessage).encode('utf-8'))
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
            conn = startClient(dest, port, True)

def readData(conn, name, port):
    while True:
        try:
            data = conn.recv()
            return data
            
        except ConnectionResetError:
            #make sure its reconnect insteaad of normal
            conn = startClient(name, port, True)
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
            if data['type'] == 'enter':
                split_msg = data['msg'].split(',')
                coin, amnt, price = split_msg[0], float(split_msg[1]), float(split_msg[2])
                current_positions.openPosition(coin, amnt, price, p_value)

            elif data['type'] == 'exit':
                split_msg = data['msg'].split(',')
                coin, amnt, price = split_msg[0], float(split_msg[1]), float(split_msg[2])
                closed_position = current_positions.closePosition(coin, amnt, price)
                if closed_position:
                    all_positions.append(closed_position)
                    coin_positions[coin].append(closed_position)
            elif data['type'] == 'portfolio_value':
                p_value = float(data['msg'])
                portfolio_datastream.update(p_value)
                current_positions.p_value = p_value

def BHSocket(bh_status):
    bh_conn = startClient('beverly_hills', os.environ['BH_PORT'])
    startInit(bh_conn, "beverly_hills", os.environ["BH_PORT"])
    while True:
        rawMsg = {'type': 'ping', 'msg':'fuck you lol', 'src':containersToId['frontend'], 'dest':containersToId['beverly_hills']}
        bh_conn.send(json.dumps(rawMsg).encode('utf-8'))
        data = readData(bh_conn, 'beverly_hills', os.environ['BH_PORT'])
        if data:
            bh_status.ping()
        time.sleep(2)

def DCSocket(dc_conn, dc_status, coin_datastreams, current_positions):
    while True:
        data = readData(dc_conn, 'main_data_consumer', os.environ['DC_PORT'])
        if data:
            data = json.loads(data)
            # print(data)
            if data['type'] == 'curPrice' and data:
                dc_status.ping()
                coin_name = data['msg']['coin'].upper()
                close_price = float(data['msg']['price'])
                
                coin_datastreams[coin_name].update(close_price)
                current_positions.updatePosition(coin_name, close_price,)


def getCoins():
    dc_conn = startClient('main_data_consumer', os.environ['DC_PORT'])
    coins = retrieveCoinData(dc_conn)
    return dc_conn, coins