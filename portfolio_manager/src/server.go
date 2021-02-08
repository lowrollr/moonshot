package main

import (
	"bufio"
	"bytes"
	"encoding/json"
	"fmt"
	"net"
	"os"

	log "github.com/sirupsen/logrus"
)

// func (client *ServerClient) Read() {
// 	for {
// 		line, err := client.reader.ReadString('\n')
// 		if err == nil {
// 			fmt.Println(line)
// 			client.outgoing <- line
// 		} else {
// 			break
// 		}
// 	}

// 	client.conn.Close()
// 	client = nil
// }

func (client *ServerClient) Write() {
	for data := range client.outgoing {
		client.writer.WriteString(data)
		client.writer.Flush()
	}
}

func (client *ServerClient) Listen() {
	// go client.Read()
	// go client.Write()
}

func (client *ServerClient) Receive() *[]byte {
	for {
		message := make([]byte, 4096)
		length, err := (*(*client).conn).Read(message)
		if err != nil {
			(*(*client).conn).Close()
			break
			//do something bettern here like a warn
		}
		//also need to do some error handling if we don't get the full message
		if length > 0 {
			trimmedMsg := bytes.Trim(message, "\x00")
			return &trimmedMsg
		}
	}
	return nil
}

func NewServerClient(connection *net.Conn) *ServerClient {
	writer := bufio.NewWriter(*connection)
	reader := bufio.NewReader(*connection)

	client := &ServerClient{
		outgoing: make(chan string),
		conn:     connection,
		reader:   reader,
		writer:   writer,
	}
	// client.Listen()

	return client
}

func ReceiveInit(frontendClient *ServerClient) bool {
	var initMsg SocketMessage
	rawBytes := (*frontendClient).Receive()
	
	if rawBytes != nil {
		err := json.Unmarshal(*rawBytes, &initMsg)
		if err != nil {
			log.Println(string(*rawBytes))
			log.Panic("Was not able to unmarshall init msg with error:", err)
		}
		if initMsg.Msg == "init" || initMsg.Msg == "'init'" || initMsg.Msg == "\"init\"" {
			log.Println("Received init message from frontend")
			return true
		}
	}
	return false
}

func startServer() *ServerClient {
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
		client := NewServerClient(&conn)

		if ReceiveInit(client) {
			return client
		}
	}
}
