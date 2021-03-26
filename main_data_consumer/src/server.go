/*
FILE: server.go
AUTHORS:
	-> Ross Copeland <rhcopeland101@gmail.com>
	-> Jacob Marshall <marshingjay@gmail.com>
WHAT:
	-> all code used in client and internal server coode
*/
package main

import (
	"sync"
	log "github.com/sirupsen/logrus"
	ws "github.com/gorilla/websocket"
)

func NewClient(connection *ws.Conn, clientId int) *Client {
	client := &Client{
		Conn: connection,
		ClientId: clientId,
	}
	return client
}

/*
	ARGS:
		-> conn (*ws.Conn): pointer to websocket connection
    RETURN:
        -> N/A
    WHAT:
		-> Hopefully on reconnect this sets up the client without a hitch because of locks
*/
func (client *Client) SetClient(conn *ws.Conn, clientId int) {
	client.ClientId = clientId
	client.Lock()
	client.Conn = conn
	client.Unlock()
}

/*
	ARGS:
		-> N/A
    RETURN:
		-> (*ws.Conn): the websocket connection of the client
*/
func (client *Client) GetClient() *ws.Conn {
	return client.Conn
}



func (client *Client) WriteMessage(msg *WebsocketMessage, wg *sync.WaitGroup){
	client.Lock()
	defer client.Unlock()
	if wg != nil {
		defer wg.Done()
	}
	err := client.GetClient().WriteJSON(msg)
	if err != nil {
		log.Warn("Was not able to write to client ", idToContainer[client.ClientId], ": ", err)
	}
}

func (client *Client) AwaitReadyMsg() {
	for {
		msg := WebsocketMessage{}
		err := client.GetClient().ReadJSON(&msg)
		if err != nil {
			log.Panic("Error reading ready message: ", err)
		} else {
			if _, ok := msg.Content["ready"]; ok {
				return
			}
		}
	}
}