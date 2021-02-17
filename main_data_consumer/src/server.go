package main

import (
	ws "github.com/gorilla/websocket"
	log "github.com/sirupsen/logrus"
)

func (client *Client) WriteSocketPriceJSON(msg *SocketPriceMessage) {
	err := client.GetClient().WriteJSON(msg)
	if err != nil {
		log.Warn(err)
	}
	return
}

func (client *Client) WriteSocketCandleJSON(msg *SocketCandleMessage) {
	err := client.GetClient().WriteJSON(msg)
	if err != nil {
		log.Warn(err)
	}
	return
}

func (client *Client) WriteSocketCoinsJSON(msg *SocketCoinMessage) {
	err := client.GetClient().WriteJSON(msg)
	if err != nil {
		log.Warn(err)
	}
	return
}

//do some error handling for if messages are sent to the right place
func (client *Client) WaitStart() {
	for {
		message := SocketMessage{}
		// var startMsg SocketMessage
		err := client.GetClient().ReadJSON(&message)
		if err != nil {
			log.Panic("Not able to parse start msg correctly. Error: " + err.Error())
		}
		if message.Msg == "start" {
			break
		}
	}
	return
}

func NewClient(connection *ws.Conn) *Client {
	client := &Client{
		// incoming: make(chan string),
		conn: connection,
	}
	return client
}

func (client *Client) SetClient(conn *ws.Conn) {
	client.Lock()
	client.conn = conn
	client.Unlock()
}

func (client *Client) GetClient() *ws.Conn {
	client.RLock()
	defer client.RUnlock()
	return client.conn
}
