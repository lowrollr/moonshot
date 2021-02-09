package main

import (
	"bufio"
	"bytes"
	"encoding/json"
	"fmt"
	"net"
	"sync"

	log "github.com/sirupsen/logrus"
)

func (client *Client) Read() {
	for {
		line, err := client.reader.ReadString('\n')
		if err == nil {
			// if client.connection != nil {
			// 	client.connection.outgoing <- line
			// }
			fmt.Println(line)
		} else {
			break
		}
	}

	client.conn.Close()
	// if client.connection != nil {
	// 	client.connection.connection = nil
	// }
	client = nil
}

func (client *Client) Write(payload []byte) {
	// client.writer.WriteString(data)
	// client.writer.Flush()

}

func (client *Client) WriteSocketMessage(payload []byte, wg *sync.WaitGroup) {
	defer wg.Done()
	var err error
	writeLen, err := client.writer.Write(payload)
	client.writer.Reset(client.writer)
	if err != nil {
		//Not able to send information
		//Try to send again or reconnect depending on the error message
	}
	for writeLen < len(payload) {
		newLength, _ := client.writer.Write(payload[writeLen:])
		writeLen += newLength
	}
	return
}

func (client *Client) Listen() {

}

func (client *Client) WaitStart() {
	//listen until start keyword
	for {
		var startMsg SocketMessage
		message := make([]byte, 1024)
		_, err := client.conn.Read(message)
		err = json.Unmarshal(bytes.Trim(message, "\x00"), &startMsg)
		if err == nil && (startMsg.Msg == "start" || startMsg.Msg == "'start'" || startMsg.Msg == "\"start\"") {
			break
		} else if err != nil && string(message) == "" {
			// client.conn.Close()
			// //try to reconnectF
			log.Println(err)
			// fmt.Println("figure out how to handle this error")
		}
	}
}

func (client *Client) Receive() *[]byte {
	retByte := make([]byte, 0)
	for {
		message := make([]byte, 4096)
		length, err := client.conn.Read(message)
		if err != nil {
			client.conn.Close()
			break
		}
		if length > 0 {
			return &message
		}
	}
	return &retByte
}

func NewClient(connection net.Conn) *Client {
	writer := bufio.NewWriter(connection)
	reader := bufio.NewReader(connection)

	client := &Client{
		// incoming: make(chan string),
		outgoing: make(chan string),
		conn:     connection,
		reader:   reader,
		writer:   writer,
		start:    false,
	}

	return client
}
