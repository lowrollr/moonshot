import socket
import time
import os
import json
import cbpro
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

def PMConnect():
    pm_conn = startClient('portfolio_manager', os.environ["PM_PORT"])
    startInit(pm_conn, "portfolio_manager", os.environ["PM_PORT"])
    return pm_conn

def PMPing(pm_conn):
    
    while True:
        ping_msg = {'type':'ping', 'msg':'fuck you lol', 'src':containersToId["frontend"], 'dest':containersToId['portfolio_manager']}
        pm_conn.send(json.dumps(ping_msg).encode('utf-8'))
        time.sleep(2)

def PMSocket(glob_status, pm_conn, pm_status, all_positions, coin_positions, current_positions, portfolio_datastream, plot_positions):
    
    p_value = 0.0
    
    while True:
        data = readData(pm_conn, 'portfolio_manager', os.environ['PM_PORT'])
        if data:
            data = json.loads(data)
            pm_status.ping()
            if data['type'] == 'pong':
                glob_status.isPaperTrading = False
            elif data['type'] == 'portfolio_value':
                glob_status.isPaperTrading = True
                account_value = float(data['msg'])
                current_positions.p_value = account_value
                portfolio_datastream.update(account_value, glob_status.lastTimestampReceived)
            elif data['type'] == 'enter':
                split_msg = data['msg'].split(',')
                coin, amnt, price = split_msg[0], float(split_msg[1]), float(split_msg[2])
                current_positions.openPosition(coin, amnt, price, glob_status.lastTimestampReceived)
                plot_positions.addNewPosition(coin, price, 'enter', glob_status.lastTimestampReceived)

            elif data['type'] == 'exit':
                split_msg = data['msg'].split(',')
                coin, amnt, price = split_msg[0], float(split_msg[1]), float(split_msg[2])
                closed_position = current_positions.closePosition(coin, amnt, price, glob_status.lastTimestampReceived)
                if closed_position:
                    all_positions.append(closed_position)
                    coin_positions[coin].append(closed_position)
                    plot_positions.addNewPosition(coin, price, 'exit', glob_status.lastTimestampReceived)
                else:
                    plot_positions.addNewPosition(coin, price, 'partial_exit', glob_status.lastTimestampReceived)
            

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

def DCSocket(glob_status, dc_conn, dc_status, coin_datastreams, current_positions):
    while True:
        data = readData(dc_conn, 'main_data_consumer', os.environ['DC_PORT'])
        if data:
            data = json.loads(data)
            # print(data)
            if data['type'] == 'curPrice' and data:
                dc_status.ping()
                coin_name = data['msg']['coin'].upper()
                close_price = float(data['msg']['price'])
                
                timestamp = int(data['msg']['time'])
                glob_status.lastTimestampReceived = timestamp
                if coin_datastreams[coin_name].initialized:
                    coin_datastreams[coin_name].update(close_price, timestamp)
                else:
                    coin_datastreams[coin_name].initialize(close_price, timestamp)
                current_positions.updatePosition(coin_name, close_price)


def getCoins():
    dc_conn = startClient('main_data_consumer', os.environ['DC_PORT'])
    coins = retrieveCoinData(dc_conn)
    return dc_conn, coins

def CBSocket(glob_status, porfolio_datastream, coin_datastreams, cur_positions, cb_status, coins):
    auth_client = cbpro.AuthenticatedClient(os.environ['COINBASE_PRO_KEY'], os.environ['COINBASE_PRO_SECRET'], os.environ['COINBASE_PRO_PASSPHRASE'], api_url="https://api-public.sandbox.pro.coinbase.com")
    accounts = auth_client.get_accounts()
    coins = set(coins)
    while True:
        if not glob_status.isPaperTrading:
            accounts = auth_client.get_accounts()
            account_value = 0.0
            for x in accounts:
                if x['currency'] in coins:
                    account_value += float(x['balance']) * coin_datastreams[x['currency']].day_data[-1][0]
                elif x['currency'] == 'USD':
                    account_value += float(x['balance'])
            if porfolio_datastream.initialized:
                porfolio_datastream.update(account_value, glob_status.lastTimestampReceived)
            else:
                porfolio_datastream.initialize(account_value, glob_status.lastTimestampReceived)
            cur_positions.p_value = account_value
        cb_status.ping()
        time.sleep(0.2)