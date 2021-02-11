package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"net"
	"os"
	"strconv"

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

func (client *ServerClient) Receive() (*[]byte, string) {
	mTypeBuff := make([]byte, 3)
	_, err := (*client.conn).Read(mTypeBuff)
	if err != nil {
		if err.Error() == "EOF" {
			t := []byte{}
			return &t, ""
		}
		log.Warn("Not able to read data type: " + err.Error())
	}
	mLenBuff := make([]byte, 10)
	_, err = (*client.conn).Read(mLenBuff)
	if err != nil {
		log.Warn("Was not able to read data len: " + err.Error())
	}

	lenString := string(mLenBuff)
	numLen, err := strconv.Atoi(lenString)
	if err != nil {
		log.Warn("Was not able to convert byte len to int: " + err.Error())
	}

	for {
		message := make([]byte, numLen)
		length, err := (*client.conn).Read(message)
		if err != nil {
			log.Warn("Was not able to read msg " + err.Error())
			break
		}
		if length > 0 {
			messageType, err := msgType(&mTypeBuff)
			if err != nil {
				log.Warn("Probably sent the wrong message type " + err.Error())
			}
			return &message, messageType
		}
	}
	return nil, ""
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
	rawBytes, msgType := (*frontendClient).Receive()

	if rawBytes != nil && msgType == "init" {
		err := json.Unmarshal(*rawBytes, &initMsg)
		if err != nil {
			log.Println(string(*rawBytes))
			log.Panic("Was not able to unmarshall init msg with error:", err)
		}
		log.Println("Received init message from frontend")
		return true
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
