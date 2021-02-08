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
		stop_candle_chan, _, err := binance.WsKlineServe(symbol, klineInterval, data.KlineDataConsumerStoreSend, ErrorTradeHandler)
		if err != nil {
			log.Warn("Was not able to open websoocket for the kline " + symbol + " with error: " + err.Error())
			printNumSockets()
		}
		<-stop_candle_chan
		log.Println("Restarting socket for obtaining minute kline data from coin: " + symbol)
		printNumSockets()
	}
}

func (data *DataConsumer) KlineDataConsumerStoreSend(event *binance.WsKlineEvent) {
	now := time.Now()
	times_per_min := 1

	//store in db
	err := Dumbo.StoreCryptoKline(event)
	if err != nil {
		log.Warn("Was not able to store kline data with error: " + err.Error())
		printNumSockets()
	}

	wg := new(sync.WaitGroup)
	wg.Add(len(data.Clients))
	for destinationStr, client := range data.Clients {
		klineMessage := SocketKlineMessage{
			Source:      "main_data_consumer",
			Destination: destinationStr,
			Msg:         event.Kline,
		}
		klineByte, _ := json.Marshal(klineMessage)
		client.WriteSocketMessage(klineByte, wg)
	}
	wg.Wait()
	EfficientSleep(times_per_min, now, time.Minute)
}

func InitConsume() {
	binance.WebsocketKeepalive = true

	binance.WebsocketTimeout = time.Second * 30
	log.SetFormatter(&log.TextFormatter{ForceColors: true, FullTimestamp: true})
}
