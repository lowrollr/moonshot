package main

import (
	"bufio"
	"encoding/json"
	"errors"
	"fmt"
	"io/ioutil"
	"net"
	"strconv"
	"sync"

	log "github.com/sirupsen/logrus"
)

func ConstructMessage(startMessage *[]byte, msgType string) (*[]byte, error) {
	numericMsgType := 0

	switch msgType {
	case "ping":
		numericMsgType = 1
	case "coinRequest":
		numericMsgType = 2
	case "coinServe":
		numericMsgType = 3
	case "init":
		numericMsgType = 4
	case "start":
		numericMsgType = 5
	case "curPrice":
		numericMsgType = 6
	case "candleStick":
		numericMsgType = 7
	default:
		return nil, errors.New("Message type " + msgType + " not supported")
	}

	startBytes := []byte(fmt.Sprintf("%03d", numericMsgType))

	midBytes := []byte(fmt.Sprintf("%010d", len(*startMessage)))

	allBytes := append(startBytes, midBytes...)
	allBytes = append(allBytes, *startMessage...)

	return &allBytes, nil
}

func msgType(typeBytes *[]byte) (string, error) {
	typeString := string((*typeBytes)[:3])
	numType, err := strconv.Atoi(typeString)
	if err != nil {
		log.Warn("Was not able to convert header to an int " + err.Error())
	}
	switch numType {
	case 1:
		return "ping", nil
	case 2:
		return "coinRequest", nil
	case 3:
		return "coinServe", nil
	case 4:
		return "init", nil
	case 5:
		return "start", nil
	case 6:
		return "curPrice", nil
	case 7:
		return "candleStick", nil
	}
	return "", errors.New("Given the wrong number of bytes. Given: " + typeString)
}

//add if there are more things in the buffer
func ParseMessage(receiveMsg *[]byte) (*[]byte, string) {
	messageType, err := msgType(receiveMsg)
	if err != nil {
		log.Warn("Was not able to parse the message type " + err.Error())
	}
	msgNoHeader := (*receiveMsg)[13:]
	return &msgNoHeader, messageType
}

func (client *Client) WriteSocketMessage(payload *[]byte, wg *sync.WaitGroup) {
	defer wg.Done()
	client.writer.Flush()
	client.WriteAll(payload)
	return
}

//do some error handling for if messages are sent to the right place
func (client *Client) WaitStart() {
	for {
		var startMsg SocketMessage
		message, err := ioutil.ReadAll(client.conn)
		if err != nil {
			log.Panic("Not able to read the start message. Error: " + err.Error())
		}
		err = json.Unmarshal(message, &startMsg)
		if err != nil {
			log.Panic("Not able to parse start msg correctly. Error: " + err.Error())
		}
		_, messageType := ParseMessage(&message)
		if messageType == "start" {
			break
		} else if err != nil && string(message) == "" {
			log.Println(err)
		}
	}
}

func (client *Client) Receive() *[]byte {
	message, err := ioutil.ReadAll(client.conn)
	if err != nil {
		log.Warn(err)
		client.conn.Close()
	}
	return &message
}

func (client *Client) WriteAll(msg *[]byte) {
	writeLen, err := client.conn.Write(*msg)
	if err != nil {
		log.Warn("An error ocurred while trying to send message: " + err.Error())
	}
	for writeLen < len(*msg) {
		newLen, err := client.conn.Write((*msg)[writeLen:])
		if err != nil {
			log.Warn("Some error happened while sending another part of message: " + err.Error())
		}
		writeLen += newLen
	}
	return
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
