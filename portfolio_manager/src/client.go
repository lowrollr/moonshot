package main

import (
	"bufio"
	"encoding/json"
	"errors"
	"fmt"
	"net"
	"strconv"
	"time"

	log "github.com/sirupsen/logrus"
)

func Receive(conn *net.Conn) (*[]byte, string) {
	mTypeBuff := make([]byte, 3)
	_, err := (*conn).Read(mTypeBuff)
	if err != nil {
		if err.Error() == "EOF" {
			t := []byte{}
			return &t, ""
		}
		log.Warn("Not able to read data type: " + err.Error())
	}
	mLenBuff := make([]byte, 10)
	_, err = (*conn).Read(mLenBuff)
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
		length, err := (*conn).Read(message)
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

func NewClient(connection *net.Conn) *Client {
	writer := bufio.NewWriter(*connection)
	reader := bufio.NewReader(*connection)

	client := &Client{
		outgoing: make(chan string),
		conn:     *connection,
		reader:   reader,
		writer:   writer,
	}
	return client
}

func ConnectServer(destination string) *net.Conn {
	const timeout = 1 * time.Minute
	//Iterating through the amount of tries to connect to database
	var err error

	for {
		conn, err := net.Dial("tcp", destination)
		if err == nil {
			log.Println("Connected to ", destination)
			return &conn
		}
		log.Printf("Could not connect to the %s with error: %s Retrying...", destination, err.Error())
		time.Sleep(time.Second * 3)
	}
	log.Panic("Could not connect to the %s with final error %s.", destination, err.Error())
	return nil

}

func startClient() map[string]*net.Conn {
	mapDomainConnection := make(map[string]*net.Conn)
	for hostname, fullUrl := range domainToUrl {
		mapDomainConnection[fullUrl] = ConnectServer(fullUrl)
		if hostname == "beverly_hills" {
			StartInit(mapDomainConnection[fullUrl])
		}
	}
	return mapDomainConnection
}

func StartRemoteServer(serverConn *net.Conn, destination_str string) {
	startMessage := SocketMessage{Msg: "",
		Source:      containerToId["portfolio_manager"],
		Destination: containerToId[destination_str]}

	for tries := 0; tries < 5; tries++ {
		writer := bufio.NewWriter(*serverConn)
		startBytes, err := json.Marshal(startMessage)
		if err != nil {
			log.Panic("could not turn SocketMessage into byte array")
		}
		writeMsg, _ := ConstructMessage(&startBytes, "start")

		writeLen, err1 := writer.Write(*writeMsg)
		_ = writer.Flush()
		if err1 != nil {
			log.Warn("Was not able to connect/write to", destination_str)
		}
		for writeLen < len(startBytes) {
			newLength, err := writer.Write((*writeMsg)[writeLen:])
			if err != nil {
				log.Warn("Was only able to send partial coin keyword to main data consumer")
			}
			writeLen += newLength
		}
		if err1 == nil && err == nil {
			return
		}
		time.Sleep(time.Second << uint(tries))
	}
	log.Panic("Was not able to send start to ", destination_str)
}

func StartInit(bevConn *net.Conn) {
	initMsg := SocketMessage{Msg: "",
		Source:      containerToId["portfolio_manager"],
		Destination: containerToId["beverly_hills"]}
	writer := bufio.NewWriter(*bevConn)
	initBytes, err := json.Marshal(initMsg)
	if err != nil {
		log.Panic("Could not turn init message into json")
	}
	writeBytes, _ := ConstructMessage(&initBytes, "init")
	writeLen, err := writer.Write(*writeBytes)
	if err != nil {
		log.Panic("Was not able to send init message to beverly hills")
	}
	for writeLen < len(initBytes) {
		newLength, err := writer.Write([]byte((*writeBytes)[writeLen:]))
		if err != nil {
			log.Panic("Was only able to send partial init keyword to beverly hills")
		}
		writeLen += newLength
	}
	writer.Flush()
}

func WriteAll(conn *net.Conn, msg *[]byte) {
	// err = conn.Flush()
	writeLen, err := (*conn).Write(*msg)
	if err != nil {
		log.Panic("Was not able to send coin keyword to main data consumer")
	}
	for writeLen < len(*msg) {
		newLength, err := (*conn).Write((*msg)[writeLen:])
		if err != nil {
			log.Panic("Was only able to send partial coin keyword to main data consumer")
		}
		writeLen += newLength
	}
}

func getCoins(dataConsConn *net.Conn) *[]string {
	coinKeyWord := SocketMessage{Msg: "",
		Source:      containerToId["portfolio_manager"],
		Destination: containerToId["main_data_consumer"]}
	for {
		coinBytes, err := json.Marshal(coinKeyWord)
		if err != nil {
			log.Panic("could not turn coins bytes into json")
		}
		writeBytes, _ := ConstructMessage(&coinBytes, "coinRequest")
		WriteAll(dataConsConn, writeBytes)

		noHeaderMsg, messageType := Receive(dataConsConn)

		if err == nil {
			var coinJson []string
			// noHeaderMsg, messageType := ParseMessage(&response)
			if messageType == "coinServe" {
				err = json.Unmarshal(*noHeaderMsg, &coinJson)
				if err != nil {
					log.Panic("Was not able to Unmarshal byte array correctly into coins")
				}
				return &coinJson
			} else {
				log.Panic("Did not send the correct message type")
			}
		}
		log.Println("Could not get coins from main dat aconsumer. Trying again. ")
		time.Sleep(3 * time.Second)
	}
	log.Panic("Could not get the coins from main data consumer")
	return nil
}
