package main

import (
	"bytes"
	"encoding/json"
	"net"
	"os"
	"strings"
	"sync"
	"time"

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

func (data *DataConsumer) ServerListen() {
	data.Clients = make(map[string]*Client)
	for {
		//change this so that it's more multithreaded. Have goroutine for each service
		// when each have been hit with start, then you can start running
		if data.NumConnections < 3 {
			log.Println("Accepting for a connection")
			conn, err := (*data.SocketServer).Accept()
			if err != nil {
				log.Panic("Could not make connection " + err.Error())
			}
			data.NumConnections++
			client := NewClient(conn)

			CoinJson, err := json.Marshal(data.Coins)
			if err != nil {
				log.Panic("Could not send coins. Stop. Error: " + err.Error())
			}

			data.Clients[conn.RemoteAddr().Network()] = client
			for {
				PMString := bytes.Trim(*client.Receive(), "\x00")
				
				if string(PMString) == "'coins'" || string(PMString) == "\"coins\"" {
					_, err := client.conn.Write(CoinJson)

					log.Println("Sent coins")
					if err != nil {
						log.Panic("Was not able to send coin data " + err.Error())
					}
					break
				}
			}
		} else {
			break
		}
	}
	//listen for start messages from all three
	wg := new(sync.WaitGroup)
	wg.Add(len(data.Clients))

	for _, client := range data.Clients {
		go client.WaitStart(wg)
	}
	wg.Wait()
}

func (data *DataConsumer) StartConsume() {
	data.Consume()
}

func (data *DataConsumer) Consume() {
	InitConsume()

	klineInterval := "1m"
	log.Println("Start Consuming")

	for _, symbol := range *data.Coins {
		symbol = strings.ToLower(symbol) + "usdt"
		go data.KlineGoRoutine(symbol, klineInterval)
	}

	log.Println("\n\nTotal Number of sockets at the beginning: ")
	printNumSockets()
	//perpetual wait
	waitFunc()
}

func (data *DataConsumer) KlineGoRoutine(symbol string, klineInterval string) {
	for {
		log.Println("Starting goroutine for getting minute kline for data of coin: " + symbol)
		stop_candle_chan, _, err := binance.WsKlineServe(symbol, klineInterval, tradeKlineDataConsumer, ErrorTradeHandler)
		if err != nil {
			log.Warn("Was not able to open websoocket for the kline " + symbol + " with error: " + err.Error())
			printNumSockets()
		}
		<-stop_candle_chan
		log.Println("Restarting socket for obtaining minute kline data from coin: " + symbol)
		printNumSockets()
	}
}

func InitConsume() {
	binance.WebsocketKeepalive = true
	binance.WebsocketTimeout = time.Second * 1

	log.SetFormatter(&log.TextFormatter{ForceColors: true, FullTimestamp: true})
}
