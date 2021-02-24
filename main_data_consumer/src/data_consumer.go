package main

import (
	"encoding/json"
	"math"
	"net/http"
	"os"
	"strconv"
	"strings"
	"sync"
	"time"

	ws "github.com/gorilla/websocket"
	log "github.com/sirupsen/logrus"
)

type DataConsumer struct {
	Clients        map[string]*Client
	Coins          *[]string
	Candlesticks   map[string]*Candlestick
	NumConnections int
}

func initDC() *DataConsumer {
	emptyClients := map[string]*Client{}
	for con, _ := range containerToId {
		if con != "main_data_consumer" {
			emptyClients[con] = &Client{}
		}
	}
	return &DataConsumer{
		Clients:        emptyClients,
		NumConnections: 0,
	}
}

func (data *DataConsumer) DBSetUp() {
	data.Coins = Dumbo.SelectCoins(-1)
	Dumbo.InitializeDB()
}

func (data *DataConsumer) WsHTTPListen() {
	http.HandleFunc("/", data.handleConnections)
	err := http.ListenAndServe(":"+string(os.Getenv("SERVERPORT")), nil)
	if err != nil {
		log.Fatal("ListenAndServe: ", err)
	}
}

func (data *DataConsumer) handleConnections(w http.ResponseWriter, r *http.Request) {
	ws, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		log.Warn("error %v", err)
	}
	message := SocketMessage{}
	_, bytes, err := ws.ReadMessage()
	if err != nil {
		log.Warn("error %v", err)
	}
	err = json.Unmarshal(bytes, &message)
	if err != nil {
		log.Warn("Was not able to unmarshall", err)
	}

	if message.Type == "coins" {
		data.Clients[idToContainer[message.Source]].SetClient(ws)
		coinMessage := SocketCoinMessageConstruct(
			data.Coins,
			containerToId["main_data_consumer"],
			message.Source,
		)
		data.Clients[idToContainer[message.Source]].
			WriteSocketCoinsJSON(coinMessage)
		data.NumConnections++
	} else if message.Type == "reconnect" {
		data.Clients[idToContainer[message.Source]].SetClient(ws)
		log.Println("Reconnected to ", idToContainer[message.Source], ws.RemoteAddr())
	} else {
		log.Println(message)
		log.Warn("Did not provide correct type")
	}
	return
}

func (data *DataConsumer) ServerListen() {
	for {
		if data.NumConnections > 2 {
			break
		}
		time.Sleep(1 * time.Second)
	}
	data.Clients["beverly_hills"].WaitStart()
}

func (data *DataConsumer) StartConsume() {
	InitConsume()
	data.Consume()
}

func (data *DataConsumer) Consume() {
	data.Candlesticks = make(map[string]*Candlestick)
	log.Println("Start Consuming")

	symbolsUSD := []string{}
	for _, sym := range *data.Coins {
		symbolsUSD = append(symbolsUSD, strings.ToUpper(sym)+"-USD")
	}
	data.SymbolWebSocket(&symbolsUSD)
}

func (data *DataConsumer) SymbolWebSocket(symbols *[]string) {
	for {
		log.Println("Starting initialization for coins: " + strings.Join(*symbols, ", "))
		symbolConn, err := InitializeSymbolSocket(symbols)
		if err != nil {
			log.Panic("Was not able to open websocket with error: " + err.Error())
		}
		data.ConsumeData(symbolConn, symbols)
	}
}

func (data *DataConsumer) ConsumeData(conn *ws.Conn, symbols *[]string) {
	for {
		message := CoinBaseMessage{}
		if err := conn.ReadJSON(&message); err != nil {
			log.Warn("Was not able to retrieve message with error: " + err.Error())
			conn.Close()
			log.Warn("Attempting to restart connection...")
			for {
				symbolConn, err := InitializeSymbolSocket(symbols)
				if err != nil {
					log.Warn("Failed to reconnect, trying again...")
					time.Sleep(1 * time.Second)
				} else {
					conn = symbolConn
					log.Warn("Reconnected!")
					break
				}
			}
		}
		if message.Type != "subscriptions" {
			data.ProcessTick(&message)
		}
	}
}

//TODO seperate into functions
func (data *DataConsumer) ProcessTick(msg *CoinBaseMessage) {
	tradePrice, _ := strconv.ParseFloat(msg.Price, 64)
	volume, _ := strconv.ParseFloat(msg.LastSize, 64)
	//send data to the frontend
	trade_coin := strings.Split(msg.ProductID, "-")[0]
	now := int64(msg.Time.Minute())

	messageToFrontend := SocketPriceMessageConstruct(
		&CoinPrice{
			Coin:  trade_coin,
			Price: tradePrice,
		},
		containerToId["main_data_consumer"],
		containerToId["frontend"],
	)
	// log.Println(messageToFrontend)

	frontendClient := data.Clients["frontend"]
	go frontendClient.WriteSocketPriceJSON(messageToFrontend)
	candle := data.Candlesticks[trade_coin]
	if candle == nil {
		data.Candlesticks[trade_coin] = &Candlestick{
			StartTime: now,
			Open:      tradePrice,
			High:      tradePrice,
			Low:       tradePrice,
			Close:     tradePrice,
			Volume:    volume,
			NumTrades: 1,
		}
	} else if candle.StartTime != now {
		wg := new(sync.WaitGroup)
		//two containers + storing in db
		wg.Add(3)
		for destinationStr, client := range data.Clients {
			if destinationStr != "frontend" {
				// log.Println(destinationStr, client)
				candleMessage := SocketAllCandleMessage{
					Source:      containerToId["main_data_consumer"],
					Destination: containerToId[destinationStr],
					Msg:         *packageToSend(&data.Candlesticks),
				}
				log.Println(candleMessage)
				go client.WriteAllSocketCandleJSON(&candleMessage, wg)
			}
		}
		//store in db
		go Dumbo.StoreAllCandles(&data.Candlesticks, wg)

		wg.Wait()

		data.Candlesticks[trade_coin] = &Candlestick{
			StartTime: now,
			Open:      tradePrice,
			High:      tradePrice,
			Low:       tradePrice,
			Close:     tradePrice,
			Volume:    volume,
			NumTrades: 1,
		}
		for _, coin := range *data.Coins {
			data.Candlesticks[coin] = &Candlestick{
				StartTime: now,
				Open:      data.Candlesticks[coin].Close,
				High:      data.Candlesticks[coin].Close,
				Low:       data.Candlesticks[coin].Close,
				Close:     data.Candlesticks[coin].Close,
				Volume:    volume,
				NumTrades: 1,
			}
		}
	} else {
		candle.Close = tradePrice
		candle.High = math.Max(candle.High, tradePrice)
		candle.Low = math.Min(candle.Low, tradePrice)
		candle.NumTrades++
		candle.Volume += volume
	}
	return
}

func InitializeSymbolSocket(symbols *[]string) (*ws.Conn, error) {
	wsConn, _, err := wsDialer.Dial("wss://ws-feed.pro.coinbase.com", nil)
	if err != nil {
		return nil, err
	}
	subscribe := CoinBaseMessage{
		Type: "subscribe",
		Channels: []MessageChannel{
			MessageChannel{
				Name:       "ticker",
				ProductIds: *symbols,
			},
		},
	}
	if err := wsConn.WriteJSON(subscribe); err != nil {
		return nil, err
	}
	return wsConn, nil
}

func InitConsume() {
	log.SetFormatter(&log.TextFormatter{ForceColors: true, FullTimestamp: true})
}
