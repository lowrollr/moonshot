package main

import (
	"bufio"
	"fmt"
	"net"
	"os"
	"sync"
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

func (client *Client) Write() {
	for data := range client.outgoing {
		client.writer.WriteString(data)
		client.writer.Flush()
	}
}

func (client *Client) Listen() {

}

func (client *Client) WaitStart(wg *sync.WaitGroup) {
	defer wg.Done()
	//listen until start keyword
	for {
		message := make([]byte, 1024)
		_, err := client.conn.Read(message)
		if err == nil && string(message) == "start" {
			break
		} else if err != nil {
			// client.conn.Close()
			// //try to reconnect
			// break
			fmt.Println("figure out how to handle this error")
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

func startServer() {
	allClients = make(map[*Client]int)
	listener, _ := net.Listen("tcp", ":"+string(os.Getenv("SERVERPORT")))
	for {
		conn, err := listener.Accept()
		if err != nil {
			fmt.Println(err.Error())
		}
		client := NewClient(conn)
		// for clientList, _ := range allClients {
		// 	if clientList.connection == nil {
		// 		client.connection = clientList
		// 		clientList.connection = client
		// 		fmt.Println("Connected")
		// 	}
		// }
		allClients[client] = 1
		fmt.Println(len(allClients))
	}
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
