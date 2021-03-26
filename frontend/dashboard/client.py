import socket
import time
import os
import json
import cbpro
import threading
from websocket import create_connection

from data import DataStream

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
                # if reconnect:
                #     rawMessage = {'type':'reconnect', 'msg':'', 'src':containersToId["frontend"], 'dest':containersToId[name]}
                #     ws.send(json.dumps(rawMessage).encode('utf-8'))
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
            rawMessage = {'content': {'ready': True}, "src":containersToId["frontend"], "dest": containersToId[dest]}
            conn.send(json.dumps(rawMessage).encode('utf-8'))
            return
        except ConnectionResetError:
            conn = startClient(dest, port, True)

def readData(conn, name, port, reconnectFn):
    reconnected = False
    while True:
        try:
            data = conn.recv()
            return conn, data, reconnected
            
        except Exception as e:
            reconnected = True
            #make sure its reconnect insteaad of normal
            print("Could not connect because of:", e)
            conn.close()
            conn = reconnectFn()
            continue

def retrieveDCData(dc_socket, coin_datastreams, portfolio_datastream, glob_status):
    coins = []
    candles = dict()
    trades = dict()
    
    dc_socket, coinMsg, _ = readData(dc_socket, 'main_data_consumer', os.environ['DC_PORT'], DCConnect)
    coins = []
    
    content = json.loads(coinMsg)["content"]
    candles = content['candles']
    coins = content['coins']
    balance_history = content['balance_history']
    
    for coin in coins:
        coin_datastreams[coin] = DataStream(name=coin)
        for candle in candles[coin]:
            close_price = candle['close']
            timestamp  = int(candle['time'] / 60)
            if coin_datastreams[coin].initialized:
                coin_datastreams[coin].update(close_price, timestamp)
            else:
                coin_datastreams[coin].initialize(close_price, timestamp)
            glob_status.lastTimestampReceived = timestamp
    for balance in balance_history:
        value = balance['Balance']
        timestamp = balance['Timestamp']
        if portfolio_datastream.initialized:
            portfolio_datastream.update(value, timestamp)
        else:
            portfolio_datastream.initialize(value, timestamp)

    print("Received coins and previous data from data consumer")
    startInit(dc_socket, "main_data_consumer", os.environ["DC_PORT"])

def PMConnect():
    pm_conn = startClient('portfolio_manager', os.environ["PM_PORT"])
    startInit(pm_conn, "portfolio_manager", os.environ["PM_PORT"])
    rawMsg = {'content': {'ping': True}, 'src':containersToId['frontend'], 'dest':containersToId['portfolio_manager']}
    pm_conn.send(json.dumps(rawMsg).encode('utf-8'))
    return pm_conn

def BHConnect():
    bh_conn = startClient('beverly_hills', os.environ['BH_PORT'])
    startInit(bh_conn, "beverly_hills", os.environ["BH_PORT"])
    rawMsg = {'content': {'ping': True}, 'src':containersToId['frontend'], 'dest':containersToId['beverly_hills']}
    bh_conn.send(json.dumps(rawMsg).encode('utf-8'))
    return bh_conn

def DCConnect():
    dc_conn = startClient('main_data_consumer', os.environ['DC_PORT'])
    rawMessage = {'content': {'candles': 1440, 'coins': True, 'balance_history':1440}, 'src':containersToId["frontend"], 'dest':containersToId['main_data_consumer']}
    dc_conn.send(json.dumps(rawMessage).encode('utf-8'))
    return dc_conn


def PMPing(pm_conn):
    
    while True:
        ping_msg = {'content': {'ping': True}, 'src':containersToId['frontend'], 'dest':containersToId['portfolio_manager']}

        try:
            pm_conn.send(json.dumps(ping_msg).encode('utf-8'))
            
        except Exception as e:
            #make sure its reconnect insteaad of normal
            print("Disconnected from PM, reconnecting... (", e, ")")
            return
            # pm_conn = PMConnect()
            # pm_conn.send(json.dumps(ping_msg).encode('utf-8'))
            
        time.sleep(2)

def PMSocket(glob_status, pm_conn, pm_status, all_positions, coin_positions, current_positions, portfolio_datastream, plot_positions, reconnectFn=PMConnect):
    
    p_value = 0.0
    pm_ping_thread = threading.Thread(target=PMPing, args=(pm_conn,))
    pm_ping_thread.start()
    while True:
        pm_conn, data, reconnected = readData(pm_conn, 'portfolio_manager', os.environ['PM_PORT'], reconnectFn)
        if reconnected:
            pm_ping_thread = threading.Thread(target=PMPing, args=(pm_conn,))
            pm_ping_thread.start()
        if data:
            content = json.loads(data)["content"]
            pm_status.ping()
            if content.get("pong"):
                glob_status.isPaperTrading = False
            elif content.get("portfolio_value"):
                glob_status.isPaperTrading = True
                account_value = float(content['portfolio_value'])
                current_positions.p_value = account_value
                if portfolio_datastream.initialized:
                    portfolio_datastream.update(account_value, glob_status.lastTimestampReceived)
                else:
                    portfolio_datastream.initialize(account_value, glob_status.lastTimestampReceived)
                for coin in plot_positions.positions_to_plot_year:
                    plot_positions.removeOldPositions(glob_status.lastTimestampReceived, coin)
            elif content.get("enter"):
                
                coin, amnt, price = content["enter"]["coin"], content["enter"]["amnt"], content["enter"]["price"]
                current_positions.openPosition(coin, amnt, price, glob_status.lastTimestampReceived)
                plot_positions.addNewPosition(coin, price, 'enter', glob_status.lastTimestampReceived)

            elif content.get("exit"):
                coin, amnt, price = content["enter"]["coin"], content["enter"]["amnt"], content["enter"]["price"]
                closed_position = current_positions.closePosition(coin, amnt, price, glob_status.lastTimestampReceived)
                if closed_position:
                    all_positions.append(closed_position)
                    coin_positions[coin].append(closed_position)
                    plot_positions.addNewPosition(coin, price, 'exit', glob_status.lastTimestampReceived)
                else:
                    plot_positions.addNewPosition(coin, price, 'partial_exit', glob_status.lastTimestampReceived)
            

def BHSocket(bh_status, reconnectFn=BHConnect):
    bh_conn = BHConnect()
    while True:
        rawMsg = {'content': {'ping': True}, 'src':containersToId['frontend'], 'dest':containersToId['beverly_hills']}
        bh_conn.send(json.dumps(rawMsg).encode('utf-8'))
        bh_conn, data, _ = readData(bh_conn, 'beverly_hills', os.environ['BH_PORT'], reconnectFn)
        if data:
            bh_status.ping()
        time.sleep(2)

def DCSocket(glob_status, dc_conn, dc_status, coin_datastreams, current_positions, reconnectFn=DCConnect):
    startInit(dc_conn, "main_data_consumer", os.environ["DC_PORT"])
    while True:
        dc_conn, data, reconnected = readData(dc_conn, 'main_data_consumer', os.environ['DC_PORT'], reconnectFn)
        if reconnected:
            if data:
                content = json.loads(data)["content"]
                candles = content['candles']
                coins = list(candles.keys())
                
                for coin in coins:
                    coin_datastreams[coin] = DataStream(name=coin)
                    for candle in candles[coin]:
                        close_price = candle['close']
                        timestamp  = int(candle['time'] / 60)
                        if coin_datastreams[coin].initialized:
                            coin_datastreams[coin].update(close_price, timestamp)
                        else:
                            coin_datastreams[coin].initialize(close_price, timestamp)
                        glob_status.lastTimestampReceived = timestamp
                        
                print("Received coins and previous data from data consumer")
                startInit(dc_conn, "main_data_consumer", os.environ["DC_PORT"])

        if data:
            content = json.loads(data)["content"]
            # print(data)
            if content.get("price"):
                dc_status.ping()
                coin_name = content["price"]["coin"].upper()
                close_price = float(content["price"]["price"])
                
                timestamp = int(content["price"]["time"] / 60) 
                glob_status.lastTimestampReceived = timestamp
                if coin_datastreams[coin_name].initialized:
                    coin_datastreams[coin_name].update(close_price, timestamp)
                else:
                    coin_datastreams[coin_name].initialize(close_price, timestamp)
                current_positions.updatePosition(coin_name, close_price)


def CBSocket(glob_status, porfolio_datastream, coin_datastreams, cur_positions, cb_status, coins):
    coinbase_url = "https://api-public.sandbox.pro.coinbase.com"
    if int(os.environ['PRODUCTION']) == 1:
        coinbase_url = "https://api.pro.coinbase.com"
    auth_client = cbpro.AuthenticatedClient(os.environ['COINBASE_PRO_KEY'], os.environ['COINBASE_PRO_SECRET'], os.environ['COINBASE_PRO_PASSPHRASE'], api_url=coinbase_url)
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