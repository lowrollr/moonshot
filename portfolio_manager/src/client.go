package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"log"
	"math"
	"net"
	"time"
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
	tries := 0

	deadline := time.Now().Add(timeout)
	var err error
	var conn net.Conn
	//Iterating through the amount of tries to connect to database
	for tries = 0; time.Now().Before(deadline); tries++ {
		conn, err = net.Dial("tcp", destination)
		if err == nil {
			return &conn
		}
		log.Printf("Could not connect to the %s with error: %s Retrying...", destination, err.Error())
		time.Sleep(time.Second << uint(tries))
	}
	log.Panic("Could not connect to the %s with final error %s", destination, err)
	return nil
}

func startClient() map[string]*net.Conn {
	mapDomainConnection := make(map[string]*net.Conn)
	for _, hostname := range domainToUrl {
		mapDomainConnection[hostname] = ConnectServer(hostname)
	}

	return mapDomainConnection
}

func getCoins(dataConsConn *net.Conn) *[]string {
	tries := 0
	coinKeyWord := "'coins'"
	for i := 0; i < 5; i++ {
		tries = i
		writer := bufio.NewWriter(*dataConsConn)
		writeLength, err := writer.Write([]byte(coinKeyWord))
		if err != nil {
			log.Panic("Was not able to send coin keyword to main data consumer")
		}
		for writeLength < 7 {
			newLength, err := writer.Write([]byte(coinKeyWord[writeLength:]))
			if err != nil {
				log.Panic("Was only able to send partial coin keyword to main data consumer")
			}
			writeLength += newLength
		}
		err = writer.Flush()
		if err != nil {
			log.Panic("Was not able to flush the buffer to the main data consumer")
		}

		
		response := []byte{}
		respLength, err := bufio.NewReader(*dataConsConn).Read(response)
		if err == nil {
			if respLength > 0 {
				coinJson := []string{}
				err = json.Unmarshal(response, coinJson)
				return &coinJson
			}
		}
		log.Println("Could not get coins from main dat aconsumer. Trying again. On try %s", tries)
		time.Sleep(time.Duration(math.Pow(float64(tries), 2)) * time.Second)
	}
	log.Panic("Could not get the coins from main data consumer")
	return nil
}
