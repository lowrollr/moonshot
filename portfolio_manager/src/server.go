package main

import (
	"bufio"
	"fmt"
	"net"
	"os"
	"strings"
)

type Client struct {
    socket net.Conn
    data   chan []byte
}

func (client *Client) receive() {
    for {
        message := make([]byte, 4096)
        length, err := client.socket.Read(message)
        if err != nil {
            client.socket.Close()
            break
        }
        if length > 0 {
            fmt.Println("RECEIVED: " + string(message))
        }
    }
}

func startClient() {
	fmt.Println("Starting client...")
	connection, err := net.Dial("tcp", "python_trade:1234")
	if err != nil {
		panic(err)
	}
	client := &Client{socket: connection}
	go client.receive()
	for {
		reader := bufio.NewReader(os.Stdin)
		message, _ := reader.ReadString('\n')
		connection.Write([]byte(strings.TrimRight(message, "\n")))
	}
}
