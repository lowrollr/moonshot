'''
FILE: server.py
AUTHORS:
    -> Jacob Marshall (marshingjay@gmail.com)
    -> Ross Copeland (rhcopeland101@gmail.com)
WHAT:
    -> This file contains functionality for the BH server
        -> processes prediction requests from PM and queries the Compute Engine for the appropriate prediction
        -> maintains ping-pong with frontend
'''

import json
from autobahn.asyncio.websocket import WebSocketServerProtocol
from vars import (
    containersToId
)

'''
CLASS: BeverlyWebSocketProtocol
WHAT:
    -> Implements a simple socket server that handles prediction requests
    -> Interfaces with the Compute Engine to retrieve predictions based on request messages
'''
class BeverlyWebSocketProtocol(WebSocketServerProtocol):

    '''
    ARGS:
        -> request (Websocket.Request): connection request from  another container
    RETURN:
        -> None
    WHAT: 
        -> Logs client connections
    '''
    def onConnect(self, request):
        print("Client connecting: {}".format(request.peer))

    '''
    ARGS:
        -> None
    RETURN:
        -> None
    WHAT: 
        -> Logs connection open
    '''
    def onOpen(self):
        print("WebSocket connection open.")

    '''
    ARGS:
        -> payload (Websocket.Message): websocket message payload from another container
        -> isBinary (bool): true if message is binary, false if  not
    RETURN:
        -> None
    WHAT: 
        -> Receives messages from other containers
        -> If the message received is a prediction request from PM, process the request and retrieve the aprropriate 
            prediction from the ComputeEngine
        
    '''
    def onMessage(self, payload, isBinary):
        # messages should not be binary!
        if isBinary:
            print("Invalid Binary Message (should be text)...")
        else:
            # load the message into a json object
            msg = json.loads(payload.decode('utf8'))

            # if the message is a prediction request from PM, process the request
            if msg['src'] == containersToId['portfolio_manager'] and msg['content'].get('predict'):
                print(f'Received prediction request: {msg["content"]["predict"]}')

                # extract the coin and timestamp from the request
                coin, timestamp = msg["content"]["predict"]["coin"], msg["content"]["predict"]["timestamp"]

                # get the prediction for the given coin from the compute engine
                prediction_result = self.factory.computeEngine.predict(coin, int(timestamp))

                # build the response body with the prediction result
                rawMsg = {'content':{'prediction': bool(prediction_result)}, 'src':containersToId['beverly_hills'], 'dest':containersToId['portfolio_manager']}
                # send the result back to PM
                self.sendMessage(json.dumps(rawMsg).encode('utf-8'))
                print(f'Sent prediction  message: {rawMsg}')

            elif msg['src'] == containersToId['frontend'] and msg['content'].get('ping'):
                # if the message is a pong from frontend, send a ping back!
                rawMsg = {'content': {'ping': True}, 'src':containersToId['beverly_hills'], 'dest':containersToId['frontend']}
                self.sendMessage(json.dumps(rawMsg).encode('utf-8'))
                
    '''
    TODO: comment this
    '''
    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {}".format(reason))

