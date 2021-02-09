package main

import (
	"bytes"
	"encoding/json"
	"math"
	"net"
	"os"
	"strconv"
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
	Candlesticks   map[string]*Candlestick
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
	data.Candlesticks = make(map[string]*Candlestick)
	klineInterval := "1m"
	log.Println("Start Consuming")

	for _, symbol := range *data.Coins {
		data.Candlesticks[strings.ToLower(symbol)] = nil
		symbol = strings.ToLower(symbol) + "usdt"
		go data.CandlestickGoRoutine(symbol, klineInterval)
	}

	log.Println("\n\nTotal Number of sockets at the beginning: ")
	printNumSockets()
	//perpetual wait
	waitFunc()
}

func (data *DataConsumer) CandlestickGoRoutine(symbol string, klineInterval string) {
	for {
		log.Println("Starting candlestick go routine for coin: " + symbol)
		stop_candle_chan, _, err := binance.WsPartialDepthServe100Ms(symbol, "5", data.BuildAndSendCandles, ErrorTradeHandler)
		if err != nil {
			log.Warn("Was not able to open websocket for " + symbol + " with error: " + err.Error())
			printNumSockets()
		}
		<-stop_candle_chan
		log.Println("Restarting candlestick socket for coin: " + symbol)
		printNumSockets()
	}
}

func (data *DataConsumer) BuildAndSendCandles(event *binance.WsPartialDepthEvent) {
	time_now := time.Now()
	now := int32(math.Trunc(float64(time_now.UnixNano()) / float64(time.Minute.Nanoseconds())))
	bid_price, _ := strconv.ParseFloat(event.Bids[0].Price, 32)
	ask_price, _ := strconv.ParseFloat(event.Asks[0].Price, 32)
	trade_price := float32((bid_price + ask_price) / 2)
	trade_coin := event.Symbol[:len(event.Symbol)-4]
	candle := data.Candlesticks[trade_coin]
	coinInfo := CoinPrice{
		coin:  trade_coin,
		price: trade_price}
	messageToFrontend := CoinDataMessage{
		Msg:         coinInfo,
		Source:      "main_data_consumer",
		Destination: "frontend"}
	wg := new(sync.WaitGroup)
	wg.Add(1)
	frontendClient := data.Clients["frontend"]
	coinPriceByte, _ := json.Marshal(messageToFrontend)
	frontendClient.WriteSocketMessage(coinPriceByte, wg)
	if candle == nil {
		data.Candlesticks[trade_coin] = &Candlestick{
			coin:      trade_coin,
			startTime: now,
			open:      trade_price,
			high:      trade_price,
			low:       trade_price,
			close:     trade_price}

	} else if candle.startTime != now {
		wg.Add(2)
		for destinationStr, client := range data.Clients {
			candleMessage := SocketCandleMessage{
				Source:      "main_data_consumer",
				Destination: destinationStr,
				Msg:         *data.Candlesticks[trade_coin],
			}
			if destinationStr != "frontend" {
				candleByte, _ := json.Marshal(candleMessage)
				client.WriteSocketMessage(candleByte, wg)
			}
		}

		data.Candlesticks[trade_coin] = &Candlestick{
			coin:      trade_coin,
			startTime: now,
			open:      trade_price,
			high:      trade_price,
			low:       trade_price,
			close:     trade_price}
	} else {
		candle.close = trade_price
		if trade_price > candle.high {
			candle.high = trade_price
		}
		if trade_price < candle.low {
			candle.low = trade_price
		}
	}
	wg.Wait()
	// store in db
	// err := Dumbo.StoreCryptoKline(event)
	// if err != nil {
	// 	log.Warn("Was not able to store kline data with error: " + err.Error())
	// 	printNumSockets()
	// }

	EfficientSleep(1, time_now, time.Second)
}

func InitConsume() {
	binance.WebsocketKeepalive = true

	binance.WebsocketTimeout = time.Second * 30
	log.SetFormatter(&log.TextFormatter{ForceColors: true, FullTimestamp: true})
}
