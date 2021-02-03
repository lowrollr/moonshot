package main

import (
	"bufio"
	"fmt"
	"log"
	"net"
	"os"
)

func (client *ServerClient) Read() {
	for {
		line, err := client.reader.ReadString('\n')
		if err == nil {
			fmt.Println(line)
			client.outgoing <- line
		} else {
			break
		}
	}

	client.conn.Close()
	client = nil
}

func (client *ServerClient) Write() {
	for data := range client.outgoing {
		client.writer.WriteString(data)
		client.writer.Flush()
	}
}

func (client *ServerClient) Listen() {
	go client.Read()
	go client.Write()
}

func (client *ServerClient) receive() {
	for {
		message := make([]byte, 4096)
		length, err := client.conn.Read(message)
		if err != nil {
			client.conn.Close()
			break
		}
		if length > 0 {
			fmt.Println("RECEIVED: " + string(message))
		}
	}
}

func NewServerClient(connection net.Conn) *ServerClient {
	writer := bufio.NewWriter(connection)
	reader := bufio.NewReader(connection)

	client := &ServerClient{
		// incoming: make(chan string),
		outgoing: make(chan string),
		conn:     connection,
		reader:   reader,
		writer:   writer,
	}
	client.Listen()

	return client
}

func startServer() *net.Conn{
	listener, err := net.Listen("tcp", ":"+string(os.Getenv("PM_PORT")))
	if err != nil {
		log.Panic("Was not able to start server on Portfolio Manager")
	}
	log.Println("Started Server on Portfolio Manager port %s", string(os.Getenv("PM_PORT")))
	for {
		conn, err := listener.Accept()
		if err != nil {
			fmt.Println(err.Error())
		}
		return &conn
	}
}
