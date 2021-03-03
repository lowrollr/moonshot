'''
FILE: server.py
AUTHORS:
    -> Ross Copeland (rhcopeland101@gmail.com)
    -> Jacob Marshall (marshingjay@gmail.com)
WHAT:
    -> This file contains functionality that implements the following:
        -> Per tick computation for indicators and model output
        -> Importing models, indicators, and features
'''

import socket
import os
import json
from threading import Thread
from autobahn.asyncio.websocket import WebSocketServerProtocol
from vars import (
    containersToId,
    idToContainer
)


class BeverlyWebSocketProtocol(WebSocketServerProtocol):

    def onConnect(self, request):
        print("Client connecting: {}".format(request.peer))

 
    def onOpen(self):
        print("WebSocket connection open.")


    def onMessage(self, payload, isBinary):
        if isBinary:
            print("Invalid Binary Message (should be text)...")
        else:
            msg = json.loads(payload.decode('utf8'))
            if msg['src'] == containersToId['portfolio_manager'] and msg['type'] == 'predict':
                print(f'Received prediction request: {msg["msg"]}')
                coin, timestamp = msg['msg'].split(',')
                prediction_result = self.factory.computeEngine.predict(coin, int(timestamp))
                rawMsg = {'type': 'prediction', 'msg':str(prediction_result), 'src':containersToId['beverly_hills'], 'dest':containersToId['portfolio_manager']}
                self.sendMessage(json.dumps(rawMsg).encode('utf-8'))
                print(f'Sent prediction  message: {rawMsg}')
            elif msg['src'] == containersToId['frontend'] and msg['type'] == 'ping':
                rawMsg = {'type': 'ping', 'msg':'fuck you too', 'src':containersToId['beverly_hills'], 'dest':containersToId['frontend']}
                self.sendMessage(json.dumps(rawMsg).encode('utf-8'))
                

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {}".format(reason))

