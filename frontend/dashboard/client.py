import socket
import time
import os
import json
import cbpro
import threading
from websocket import create_connection
from datetime import datetime
from collections import deque

from data import (
    DataStream,
    Positions,
    Position,
    PositionStream,
    Status, 
    PlotPositions
)

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
    candles = content['dwmy_prices']
    coins = content['coins']
    balance_history = content['dwmy_balance_history']
    open_position_trades = content['open_trades']
    past_trades = content['trade_history']

    cur_positions = Positions(coins)
    position_history = PositionStream(coins)
    plot_positions = PlotPositions(coins)

    for coin in coins:
        coin_datastreams[coin] = DataStream(name=coin)
        if candles[coin]["d"]:
            coin_datastreams[coin].day_data = deque(maxlen=1440)
            coin_datastreams[coin].initialized = True
            for candle in candles[coin]["d"]:
                close_price = candle['close']
                timestamp  = int(candle['timestamp'] / 60)
                timestamp_str = datetime.fromtimestamp(timestamp*60).strftime('%Y-%m-%d %H:%M:%S')
                coin_datastreams[coin].day_data.append((close_price, timestamp, timestamp_str))
                coin_datastreams[coin].last_updated_day = timestamp
                
            glob_status.lastTimestampReceived = timestamp
        if candles[coin]["w"]:
            coin_datastreams[coin].week_data = deque(maxlen=1440)
            for candle in candles[coin]["w"]:
                close_price = candle['close']
                timestamp  = int(candle['timestamp'] / 60)
                timestamp_str = datetime.fromtimestamp(timestamp*60).strftime('%Y-%m-%d %H:%M:%S')
                coin_datastreams[coin].week_data.append((close_price, timestamp, timestamp_str))
                coin_datastreams[coin].last_updated_week = timestamp
        if candles[coin]["m"]:
            coin_datastreams[coin].month_data = deque(maxlen=1440)
            for candle in candles[coin]["m"]:
                close_price = candle['close']
                timestamp  = int(candle['timestamp'] / 60)
                timestamp_str = datetime.fromtimestamp(timestamp*60).strftime('%Y-%m-%d %H:%M:%S')
                coin_datastreams[coin].month_data.append((close_price, timestamp, timestamp_str))
                coin_datastreams[coin].last_updated_month = timestamp
        if candles[coin]["y"]:
            coin_datastreams[coin].year_data = deque(maxlen=1440)
            for candle in candles[coin]["y"]:
                close_price = candle['close']
                timestamp  = int(candle['timestamp'] / 60)
                timestamp_str = datetime.fromtimestamp(timestamp*60).strftime('%Y-%m-%d %H:%M:%S')
                coin_datastreams[coin].year_data.append((close_price, timestamp, timestamp_str))
                coin_datastreams[coin].last_updated_year = timestamp
                
    if balance_history["d"]:
        portfolio_datastream.day_data = deque(maxlen=1440)
        portfolio_datastream.initialized = True
        for balance in balance_history["d"]:
            value = balance['Balance']
            timestamp = int(balance['Timestamp'] / 60)
            timestamp_str = datetime.fromtimestamp(timestamp*60).strftime('%Y-%m-%d %H:%M:%S')
            portfolio_datastream.day_data.append((value, timestamp, timestamp_str))
            portfolio_datastream.last_updated_day = timestamp
    if balance_history["w"]:
        portfolio_datastream.week_data = deque(maxlen=1440)
        for balance in balance_history["w"]:
            value = balance['Balance']
            timestamp = int(balance['Timestamp'] / 60)
            timestamp_str = datetime.fromtimestamp(timestamp*60).strftime('%Y-%m-%d %H:%M:%S')
            portfolio_datastream.week_data.append((value, timestamp, timestamp_str))
            portfolio_datastream.last_updated_week = timestamp
    if balance_history["m"]:
        portfolio_datastream.month_data = deque(maxlen=1440)
        for balance in balance_history["m"]:
            value = balance['Balance']
            timestamp = int(balance['Timestamp'] / 60)
            timestamp_str = datetime.fromtimestamp(timestamp*60).strftime('%Y-%m-%d %H:%M:%S')
            portfolio_datastream.month_data.append((value, timestamp, timestamp_str))
            portfolio_datastream.last_updated_month = timestamp
    if balance_history["y"]:
        portfolio_datastream.year_data = deque(maxlen=1440)
        for balance in balance_history["y"]:
            value = balance['Balance']
            timestamp = int(balance['Timestamp'] / 60)
            timestamp_str = datetime.fromtimestamp(timestamp*60).strftime('%Y-%m-%d %H:%M:%S')
            portfolio_datastream.year_data.append((value, timestamp, timestamp_str))
            portfolio_datastream.last_updated_year = timestamp
    for coin in coins:
        for trade in open_position_trades[coin]:
            timestamp = int(trade['Timestamp'] / 60)
            if int(trade['TypeId']) == 0:
                enter_price = float(trade['ExecutedValue'])/float(trade['Units'])
                cur_positions.openPosition(coin, float(trade['Units']), enter_price, timestamp)
                plot_positions.addNewPosition(coin, enter_price, 'enter', timestamp)
            elif int(trade['TypeId']) == 1:
                exit_price = float(trade['ExecutedValue'])/float(trade['Units'])
                cur_positions.closePosition(coin, float(trade['Units']), exit_price, timestamp)
                plot_positions.addNewPosition(coin, exit_price, 'partial_exit', timestamp)

    all_past_positions = []
    for coin in coins:
        enter_price = 0.0
        time_entered = 0
        amnt = 0
        alloc = 0
        for trade in past_trades[coin]:
            price = float(trade['ExecutedValue'])/float(trade['Units'])
            timestamp = int(trade['Timestamp'] / 60)
            if trade['TypeId'] == 0:
                plot_positions.addNewPosition(coin, price, 'enter', timestamp)
                enter_price = price
                time_entered = timestamp
                amnt = float(trade['Units'])
            elif trade['TypeId'] == 1:
                plot_positions.addNewPosition(coin, price, 'partial_exit', timestamp)
            else:
                plot_positions.addNewPosition(coin, price, 'exit', timestamp)
                past_position = Position(coin, time_entered, enter_price, price, amnt, price*amnt, timestamp)
                all_past_positions.append(past_position)
                position_history.coin_positions[coin].append(past_position)
    all_past_positions.sort(key=lambda x: x.exit_time, reverse=False)
    for position in all_past_positions:
        position_history.all_positions.append(position)

    print("Received coins and previous data from data consumer")
    startInit(dc_socket, "main_data_consumer", os.environ["DC_PORT"])
    return cur_positions, position_history, plot_positions

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
    rawMessage = {'content': {'dwmy_prices': True, 'coins': True, 'dwmy_balance_history':True, 'open_trades': True, 'trade_history': 20}, 'src':containersToId["frontend"], 'dest':containersToId['main_data_consumer']}
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
            for coin in plot_positions.positions_to_plot_year:
                plot_positions.removeOldPositions(glob_status.lastTimestampReceived, coin)
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
                
            elif content.get("enter"):
                
                coin, amnt, price = content["enter"]["coin"], float(content["enter"]["amnt"]), float(content["enter"]["price"])
                current_positions.openPosition(coin, amnt, price, glob_status.lastTimestampReceived)
                plot_positions.addNewPosition(coin, price, 'enter', glob_status.lastTimestampReceived)

            elif content.get("exit"):
                coin, amnt, price = content["exit"]["coin"], float(content["exit"]["amnt"]), float(content["exit"]["price"])
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


def CBSocket(glob_status, portfolio_datastream, coin_datastreams, cur_positions, cb_status, coins):
    coinbase_url = "https://api-public.sandbox.pro.coinbase.com"
    if int(os.environ['PRODUCTION']) == 1:
        coinbase_url = "https://api.pro.coinbase.com"
    auth_client = cbpro.AuthenticatedClient(os.environ['COINBASE_PRO_KEY'], os.environ['COINBASE_PRO_SECRET'], os.environ['COINBASE_PRO_PASSPHRASE'], api_url=coinbase_url)
    accounts = auth_client.get_accounts()
    coins = set(coins)
    while True:
        try:
            if not glob_status.isPaperTrading:
                accounts = auth_client.get_accounts()
                account_value = 0.0
                for x in accounts:
                    if x['currency'] in coins:
                        account_value += float(x['balance']) * coin_datastreams[x['currency']].day_data[-1][0]
                    elif x['currency'] == 'USD':
                        account_value += float(x['balance'])
                if portfolio_datastream.initialized:
                    portfolio_datastream.update(account_value, glob_status.lastTimestampReceived)
                else:
                    portfolio_datastream.initialize(account_value, glob_status.lastTimestampReceived)
                cur_positions.p_value = account_value
            cb_status.ping()
            time.sleep(0.2)
        except Exception as exception:
            print("Exception occured in CB socket thread: " + exception + ", Resetting connection!")
            auth_client = cbpro.AuthenticatedClient(os.environ['COINBASE_PRO_KEY'], os.environ['COINBASE_PRO_SECRET'], os.environ['COINBASE_PRO_PASSPHRASE'], api_url=coinbase_url)

