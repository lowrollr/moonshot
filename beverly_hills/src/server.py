import socket
import os
import json
from threading import Thread
from autobahn.asyncio.websocket import WebSocketServerProtocol

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
            # if msg['type'] == 'predict':
            #     print(msg['msg'])
            #     prediction_result = self.factory.computeEngine.predict(*msg['msg'])
            #     self.sendMessage()


    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {}".format(reason))


# def computeResult(model, data):
    