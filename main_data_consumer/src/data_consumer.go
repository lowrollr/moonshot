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

	"github.com/gorilla/websocket"
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

func (data *DataConsumer) SendPriceContainers(*binance.WsTradeEvent) {
	//Send out data to the rest of the containers
}

func (data *DataConsumer) Consume() {
	//maybe data class var?
	var SymbolSockets map[string]*websocket.Conn

	InitConsume()
	log.Println("Start Consuming")
	for _, symbol := range *data.Coins {
		data.Candlesticks[symbol] = nil
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

func (data *DataConsumer) KlineDataConsumerStoreSend(event *binance.WsTradeEvent) {
	now := int32(math.Trunc(float64(time.Now().UnixNano()) / float64(time.Minute.Nanoseconds())))
	trade_price_fl64, _ := strconv.ParseFloat(event.Price, 32)
	trade_price := float32(trade_price_fl64)
	trade_coin := event.Symbol[:len(event.Symbol)-4]
	candle := data.Candlesticks[trade_coin]
	if candle == nil {
		data.Candlesticks[trade_coin] = &Candlestick{
			coin:      trade_coin,
			startTime: now,
			open:      trade_price,
			high:      trade_price,
			low:       trade_price,
			close:     trade_price}
	} else if candle.startTime != now {
		wg := new(sync.WaitGroup)
		wg.Add(len(data.Clients))
		for destinationStr, client := range data.Clients {
			klineMessage := SocketKlineMessage{
				Source:      "main_data_consumer",
				Destination: destinationStr,
				Msg:         *data.Candlesticks[trade_coin],
			}
			if destinationStr == "frontend" {
				log.Println(klineMessage)
			}
			klineByte, _ := json.Marshal(klineMessage)
			client.WriteSocketMessage(klineByte, wg)
		}
		wg.Wait()
		log.Println(event)
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
	//store in db
	// err := Dumbo.StoreCryptoKline(event)
	// if err != nil {
	// 	log.Warn("Was not able to store kline data with error: " + err.Error())
	// 	printNumSockets()
	// }

	// EfficientSleep(times_per_min, now, time.Second)
}

func InitConsume() {
	binance.WebsocketKeepalive = true

	binance.WebsocketTimeout = time.Second * 30
	log.SetFormatter(&log.TextFormatter{ForceColors: true, FullTimestamp: true})
}
