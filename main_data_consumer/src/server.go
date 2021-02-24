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

	ws "github.com/gorilla/websocket"
	log "github.com/sirupsen/logrus"
)

/*
	ARGS:
		-> msg (*SocketPriceMessage): Pointer to Price message
    RETURN:
        -> N/A
    WHAT:
		-> Sends price info with lock so many goroutines can use it
*/
func (client *Client) WriteSocketPriceJSON(msg *SocketPriceMessage) {
	client.Lock()
	defer client.Unlock()
	err := client.conn.WriteJSON(msg)
	if err != nil {
		log.Warn(err)
	}
	return
}

/*
	ARGS:
		-> msg (*SocketCandleMessage): candle object
    RETURN:
        -> N/A
    WHAT:
		-> sends candle data
*/
func (client *Client) WriteSocketCandleJSON(msg *SocketCandleMessage) {
	err := client.GetClient().WriteJSON(msg)
	if err != nil {
		log.Warn(err)
	}
	return
}

/*
	ARGS:
		-> msg (*SocketAllCandleMessage): Many Candle message to send
		-> wg (*sync.WaitGroup): used for concurrency
    RETURN:
        -> N/A
    WHAT:
		-> Sends multiple candle message with waitgroup for concurrency
*/
func (client *Client) WriteAllSocketCandleJSON(msg *SocketAllCandleMessage, wg *sync.WaitGroup) {
	defer wg.Done()
	err := client.GetClient().WriteJSON(msg)
	if err != nil {
		log.Warn(err)
	}
	return
}

/*
	ARGS:
		-> msg (*SocketCoinMessage): pointer to coin message object
    RETURN:
        -> N/A
    WHAT:
		-> sends coins json message
*/
func (client *Client) WriteSocketCoinsJSON(msg *SocketCoinMessage) {
	err := client.GetClient().WriteJSON(msg)
	if err != nil {
		log.Warn(err)
	}
	return
}

/*
	ARGS:
		-> N/A
    RETURN:
        -> N/A
    WHAT:
		-> Function to wait until it gets a start message to consume
	TODO:
		-> do some error handling for if messages are sent to the right place
*/
func (client *Client) WaitStart() {
	for {
		message := SocketMessage{}
		// var startMsg SocketMessage
		err := client.GetClient().ReadJSON(&message)
		if err != nil {
			log.Panic("Not able to parse start msg correctly. Error: " + err.Error())
		}
		if message.Type == "start" {
			break
		}
	}
	return
}

/*
	ARGS:
		-> connection (*ws.Conn): pointer to a websocket connection
    RETURN:
        -> (*Client): pointer to Client object
    WHAT:
		-> creates a client object
*/
func NewClient(connection *ws.Conn) *Client {
	client := &Client{
		conn: connection,
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
func (client *Client) SetClient(conn *ws.Conn) {
	client.Lock()
	client.conn = conn
	client.Unlock()
}

/*
	ARGS:
		-> N/A
    RETURN:
		-> (*ws.Conn): the websocket connection of the client
    WHAT:
		-> retrieves the websocket connection of client with reader locks
*/
func (client *Client) GetClient() *ws.Conn {
	client.RLock()
	defer client.RUnlock()
	return client.conn
}