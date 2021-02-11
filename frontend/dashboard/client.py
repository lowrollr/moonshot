import socket
import time
import os
import json
from vars import (
    containersToId,
    idToContainer
)

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

def constructMsg(rawMsg, msgType):
    tMsg = 0
    rawBytesMsg = bytes(rawMsg, encoding="utf-8")
    if msgType == "ping":
        tMsg = 1
    elif msgType == "coinRequest":
        tMsg = 2
    elif msgType == "coinServe":
        tMsg = 3
    elif msgType == "init":
        tMsg = 4
    elif msgType == "start":
        tMsg = 5
    elif msgType == "curPrice":
        tMsg = 6
    elif msgType == "candleStick":
        tMsg = 7
    else:
        raise ValueError(f"The message type is not defined: {msgType}")

    startBytes = bytes(str(tMsg).rjust(3, '0'), encoding='utf-8')
    midBytes = bytes(str(len(rawBytesMsg)).rjust(10, '0'), encoding='utf-8')
    return startBytes + midBytes + rawBytesMsg

def startInit(conn, dest, port):
    while True:
        try:
            rawMessage = {"msg": "", "src":containersToId["frontend"], "dest": containersToId[dest]}
            bytesMsg = constructMsg(json.dumps(rawMessage), "init")
            conn.sendall(bytes(bytesMsg))
            return
        except ConnectionResetError:
            conn = startClient(dest, port)

def parseMsgType(byteType):
    numType = int(byteType)
    if numType == 1:
        return "ping"
    elif numType == 2:
        return "coinRequest"
    elif numType == 3:
        return "coinServe"
    elif numType == 4:
        return "init"
    elif numType == 5:
        return "start"
    elif numType == 6:
        return "curPrice"
    elif numType == 7:
        return "candleStick"
    else:
        raise ValueError("Num type is not defined: " + str(numType))

def readData(conn, name, port):
    while True:
        try:
            msgType = conn.recv(3)
            if len(msgType) == 0:
                return b'', ""
            #do stuff with message type
            msgLen = int(conn.recv(10))
            #should change this because this could be ridiculous number
            # making it really slow
            data = conn.recv(msgLen)

            return data, parseMsgType(msgType)
            
        except ConnectionResetError:
            conn = startClient(name, port)
            continue

def retrieveCoinData(dc_socket):
    coins = ""
    while True:
        rawMessage = {'msg':'', 'src':containersToId["frontend"], 'dest':containersToId['main_data_consumer']}
        bytesMsg = constructMsg(json.dumps(rawMessage), 'coinRequest')
        dc_socket.sendall(bytesMsg)
        coins, messageType = readData(dc_socket, 'main_data_consumer', os.environ['DC_PORT'])
        
        if messageType == "coinServe":
            coins = json.loads(coins.decode('utf-8'))
        if len(coins) > 0:
            break
    print("Received coins from data consumer")
    return coins

def PMSocket(pm_status, portfolio_datastream, all_positions, coin_positions, current_positions):
    pm_conn = startClient('portfolio_manager', os.environ["PM_PORT"])
    startInit(pm_conn, "portfolio_manager", os.environ["PM_PORT"])
    p_value = 0.0
    
    while True:
        data, data_msg_type = readData(pm_conn, 'beverly_hills', os.environ['BH_PORT'])
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
        data, data_msg_type = readData(bh_conn, 'beverly_hills', os.environ['BH_PORT'])
        if data:
            bh_status.ping()

def DCSocket(dc_conn, dc_status, coin_datastreams):
    while True:
        data, data_msg_type = readData(dc_conn, 'main_data_consumer', os.environ['DC_PORT'])
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