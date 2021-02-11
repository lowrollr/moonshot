package main

import (
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
	if err != nil {
		log.Panic(err)
	}
	data.SocketServer = &listener
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
	CoinByte, err := json.Marshal(data.Coins)
	if err != nil {
		log.Panic("Could not convert coins to Json. Stop. Error: " + err.Error())
	}

	for data.NumConnections < 3 {
		//change this so that it's more multithreaded. Have goroutine for each service
		// when each have been hit with start, then you can start running
		log.Println("Waiting for a connection...")
		conn, err := (*data.SocketServer).Accept()
		if err != nil {
			log.Panic("Could not make connection " + err.Error())
		}
		client := NewClient(conn)
		
		for {
			msgContent, messageType := client.Receive()
			if len(*msgContent) == 0 {
				conn.Close()
				break
			}
			if messageType == "coinRequest" {
				var ClientJson SocketMessage
				err = json.Unmarshal(*msgContent, &ClientJson)
				if err != nil {
					log.Warn("Was not able to unmarshall the client coin request " + err.Error())
				}
				writeMsg, err := ConstructMessage(&CoinByte, "coinServe")
				if err != nil {
					log.Panic("There is no message type defined provided")
				}
				client.WriteAll(writeMsg)
				log.Println("Sent coins to ", ClientJson.Source, conn.RemoteAddr())

				data.Clients[idToContainer[ClientJson.Source]] = client
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
	InitConsume()
	data.Consume()
}

func (data *DataConsumer) Consume() {
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
	messageToFrontend := CoinDataMessage{
		Msg: CoinPrice{
			Coin:  trade_coin,
			Price: trade_price},
		Source:      containerToId["main_data_consumer"],
		Destination: containerToId["frontend"]}
	wg := new(sync.WaitGroup)
	wg.Add(1)
	frontendClient := data.Clients["frontend"]
	coinPriceByte, _ := json.Marshal(messageToFrontend)
	writeBytes, _ := ConstructMessage(&coinPriceByte, "curPrice")
	go frontendClient.WriteSocketMessage(writeBytes, wg)
	if candle == nil {
		data.Candlesticks[trade_coin] = &Candlestick{
			Coin:      trade_coin,
			StartTime: now,
			Open:      trade_price,
			High:      trade_price,
			Low:       trade_price,
			Close:     trade_price}
	} else if candle.StartTime != now {
		wg.Add(2)
		for destinationStr, client := range data.Clients {
			candleMessage := SocketCandleMessage{
				Source:      containerToId["main_data_consumer"],
				Destination: containerToId[destinationStr],
				Msg:         *data.Candlesticks[trade_coin],
			}
			if destinationStr != "frontend" {
				candleByte, _ := json.Marshal(candleMessage)
				writeBytes, _ = ConstructMessage(&candleByte, "candleStick")
				go client.WriteSocketMessage(writeBytes, wg)
			}
		}
		data.Candlesticks[trade_coin] = &Candlestick{
			Coin:      trade_coin,
			StartTime: now,
			Open:      trade_price,
			High:      trade_price,
			Low:       trade_price,
			Close:     trade_price}
	} else {
		candle.Close = trade_price
		if trade_price > candle.High {
			candle.High = trade_price
		}
		if trade_price < candle.Low {
			candle.Low = trade_price
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
