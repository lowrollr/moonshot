package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"net"
	"time"

	log "github.com/sirupsen/logrus"
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

func NewClient(connection *net.Conn) *Client {
	writer := bufio.NewWriter(*connection)
	reader := bufio.NewReader(*connection)

	client := &Client{
		outgoing: make(chan string),
		conn:     *connection,
		reader:   reader,
		writer:   writer,
	}
	// client.Listen()

	return client
}

func ConnectServer(destination string) *net.Conn {
	const timeout = 1 * time.Minute
	//Iterating through the amount of tries to connect to database
	var err error

	for {
		conn, err := net.Dial("tcp", destination)
		if err == nil {
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
	for _, hostname := range domainToUrl {
		mapDomainConnection[hostname] = ConnectServer(hostname)
	}
	return mapDomainConnection
}

func StartRemoteServer(serverConn *net.Conn, destination_str string) {
	startMessage := SocketMessage{Msg: "start", Source: "portfolio_manager", Destination: destination_str}
	for tries := 0; tries < 5; tries++ {
		writer := bufio.NewWriter(*serverConn)
		startBytes, err := json.Marshal(startMessage)
		if err != nil {
			log.Panic("could not turn SocketMessage into byte array")
		}
		writeLen, err1 := writer.Write(startBytes)
		_ = writer.Flush()
		if err1 != nil {
			log.Warn("Was not able to connect/write to", destination_str)
		}
		for writeLen < len(startBytes) {
			newLength, err := writer.Write(startBytes[writeLen:])
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

func getCoins(dataConsConn *net.Conn) *[]string {

	coinKeyWord := SocketMessage{Msg: "coins", Source: "portfolio_manager", Destination: "main_data_consumer"}
	for {

		writer := bufio.NewWriter(*dataConsConn)
		coinBytes, err := json.Marshal(coinKeyWord)
		if err != nil {
			log.Panic("could not turn coins word into json")
		}
		writeLength, err := writer.Write(coinBytes)
		if err != nil {
			log.Panic("Was not able to send coin keyword to main data consumer")
		}
		for writeLength < 5 {
			newLength, err := writer.Write([]byte(coinBytes[writeLength:]))
			if err != nil {
				log.Panic("Was only able to send partial coin keyword to main data consumer")
			}
			writeLength += newLength
		}
		err = writer.Flush()
		if err != nil {
			log.Panic("Was not able to flush the buffer to the main data consumer")
		}

		response, err := bufio.NewReader(*dataConsConn).ReadBytes('\x00')
		if err == nil {
			var coinJson []string
			response = response[:len(response)-1]
			err = json.Unmarshal([]byte(response), &coinJson)
			return &coinJson
		}
		log.Println("Could not get coins from main dat aconsumer. Trying again. ")
		time.Sleep(3 * time.Second)
	}
	log.Panic("Could not get the coins from main data consumer")
	return nil
}
