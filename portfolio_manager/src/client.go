package main

import (
	"bufio"
	"fmt"
	"net"
	"os"
)

func (client *Client) Write() {
	for data := range client.outgoing {
		client.writer.WriteString(data)
		client.writer.Flush()
	}
}

func (client *Client) Read() {
	for {
		line, err := client.reader.ReadString('\n')
		if err == nil {
			fmt.Println(line)
			client.outgoing <- line
			client.Write()
		} else {
			break
		}
	}

	client.conn.Close()
	client = nil
}

//subject to change
func (client *Client) Listen() {
	go client.Read()
	// go client.Write()
}

func NewClient(connection net.Conn) *Client {
	writer := bufio.NewWriter(connection)
	reader := bufio.NewReader(connection)

	client := &Client{
		outgoing: make(chan string),
		conn:     connection,
		reader:   reader,
		writer:   writer,
	}
	client.Listen()

	return client
}

func startClient() {
	// conn, err := net.Dial("tcp", "strategy_manager:" + string(os.Getenv("STRATPORT")))
	conn, err := net.Dial("tcp", "main_data_consumer:"+string(os.Getenv("DATAPORT")))

	// conn, err := net.Dial("tcp", "main_data_consumer:" + string(os.Getenv("DATAPORT")))
	if err != nil {
		panic(err)
	}
	_ = NewClient(conn)

}
