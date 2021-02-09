package main

import (
	"bytes"
	"encoding/json"
	"net"
	"os"
	"strings"
	"sync"
	"time"

	"github.com/gorilla/websocket"
	"github.com/ross-hugo/go-binance/v2"
	log "github.com/sirupsen/logrus"
)

type DataConsumer struct {
	SocketServer   *net.Listener
	NumConnections int
	Clients        map[string]*Client
	Coins          *[]string
}

func (data *DataConsumer) InitializeServer(wg *sync.WaitGroup) {
	defer wg.Done()
	listener, err := net.Listen("tcp", ":"+string(os.Getenv("SERVERPORT")))
	data.SocketServer = &listener
	if err != nil {
		log.Panic(err)
	}
	data.NumConnections = 0
}

func (data *DataConsumer) SyncSetUp() {
	data.Coins = Dumbo.SelectCoins(-1)
	wg := new(sync.WaitGroup)
	wg.Add(2)

	go data.InitializeServer(wg)
	go Dumbo.InitializeDB(wg)

	wg.Wait()
}

func (data *DataConsumer) SendCoins() {

}

func (data *DataConsumer) ServerListen() {
	data.Clients = make(map[string]*Client)

	for data.NumConnections < 3 {
		//change this so that it's more multithreaded. Have goroutine for each service
		// when each have been hit with start, then you can start running
		log.Println("Waiting for a connection...")
		conn, err := (*data.SocketServer).Accept()
		if err != nil {
			log.Panic("Could not make connection " + err.Error())
		}

		client := NewClient(conn)

		CoinJson, err := json.Marshal(data.Coins)
		if err != nil {
			log.Panic("Could not send coins. Stop. Error: " + err.Error())
		}

		for {
			ClientBytes := bytes.Trim(*client.Receive(), "\x00")
			if len(ClientBytes) == 0 {
				conn.Close()
				break
			}

			var ClientJson SocketMessage
			err = json.Unmarshal(ClientBytes, &ClientJson)

			if ClientJson.Msg == "'coins'" || ClientJson.Msg == "\"coins\"" || ClientJson.Msg == "coins" {
				CoinJson = append(CoinJson, '\x00')
				_, err := client.conn.Write(CoinJson)

				if err != nil {
					log.Panic("Was not able to send coin data " + err.Error())
				}
				log.Println("Sent coins to ", ClientJson.Source, conn.RemoteAddr())

				data.Clients[ClientJson.Source] = client
				data.NumConnections++
				break
			}
		}
	}
	//listen for start messages from all three

	for source, client := range data.Clients {
		if source == "beverly_hills" {
			client.WaitStart()
		}
	}
}

func (data *DataConsumer) StartConsume() {
	data.Consume()
}

func (data *DataConsumer) SendPriceContainers(*binance.WsTradeEvent) {
	//Send out data to the rest of the containers
}

func (data *DataConsumer) Consume() {
	//maybe data class var?
	var SymbolSockets map[string]*websocket.Conn

	InitConsume()

	log.Println("Start Consuming")
	for _, symbol := range *data.Coins {
		symbol = strings.ToLower(symbol) + "usdt"
		conn, err := binance.SocketTradeServe(symbol)
		if err != nil {
			//do something
		}
		SymbolSockets[symbol] = conn
	}

	for {
		//One problem with this is how to recover if there is a shut down of the socket ex: broken pipe or something
		startTime := time.Now()
		for _, socket := range SymbolSockets {
			tradeEvent := binance.ReadSocket(socket)
			//construct kline here
			data.SendPriceContainers(tradeEvent)
			
			//check if should send and reset the custum klines
			//true is just placeholder actually check if it has been a minute
			if true {
				//Store in database
				//Send to containers the kline instead of just price now
			}
		}

		EfficientSleep(2, startTime, time.Second)
	}
}

func InitConsume() {
	binance.WebsocketKeepalive = true

	binance.WebsocketTimeout = time.Second * 30
	log.SetFormatter(&log.TextFormatter{ForceColors: true, FullTimestamp: true})
}
