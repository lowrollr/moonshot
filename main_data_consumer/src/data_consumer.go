/*
FILE: data_consumer.go
AUTHORS:
	-> Jacob Marshall <marshingjay@gmail.com>
	-> Ross Copeland <rhcopeland101@gmail.com>
WHAT:
	-> This contains core functionality of the data consumer
	-> functions that don't have an obvious other home and implement something essential to DC functionality live here
*/
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
	"gorm.io/gorm"
	ws "github.com/gorilla/websocket"
	log "github.com/sirupsen/logrus"
)

/*
	ARGS:
        -> Clients: the clients connected to the data consumer socket server
		-> Coins: names of coins we are trading
		-> Candlesticks: place to store candlestick data we are computing
		-> NumConnecitons: for initializtion of how many containers connect
    WHAT:
		-> struct for most "global" thigs in data consumer
*/
type DataConsumer struct {
	Clients        map[string]*Client
	Coins          *[]string
	Candlesticks   map[string]*Candlestick
	CandlesticksQueue map[string][]Candlestick
	CandlesInQueue bool
	Database	   *gorm.DB
	ConnectionsReady int
}

/*
	ARGS:
        -> N/A
    RETURN:
        -> a DataConsumer pointer
    WHAT:
		-> Initializes core data consumer object
		-> Initializes websocket client objects for each other container
*/
func InitDataConsumer() *DataConsumer {
	log.SetFormatter(&log.TextFormatter{ForceColors: true, FullTimestamp: true})
	clients := make(map[string]*Client)
	//  return an instantiatized DataConsumer struct
	return &DataConsumer{
		Coins: 			RetrieveCoins(),
		Clients:        clients,
		ConnectionsReady: 0,
		CandlesInQueue: false,
		CandlesticksQueue: make(map[string][]Candlestick),
		Candlesticks: make(map[string]*Candlestick),
	}
	
}



/*
	ARGS:
        -> N/A
    RETURN:
        -> N/A
    WHAT:
		-> Function that starts web server that handles any WS connections
		-> Run in goroutine because we're alwayas listening (reconnects)
*/
func (dc *DataConsumer) WsHTTPListen() {
	http.HandleFunc("/", dc.HandleConnections)
	err := http.ListenAndServe(":"+string(os.Getenv("SERVERPORT")), nil)
	if err != nil {
		log.Fatal("ListenAndServe: ", err)
	}
}


/*
	ARGS:
        -> w (http.ResponseWriter):
		-> r (*http.Request):
    RETURN:
        -> N/A
    WHAT:
		-> Handles incoming websocket connections
		-> each connection will send a json-packaged message specifying the data
			that should be sent back
			-> most containers will request historical data on startup to fill data queues
*/
func (dc *DataConsumer) HandleConnections(w http.ResponseWriter, r *http.Request) {

	// first, upgrade the http connection to a websocket connection
	websocket, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		log.Panic("Error upgrading server to websocket: ", err)
	}

	// read the initial message sent on the connection
	_, messageBytes, err := websocket.ReadMessage()
	if err != nil {
		log.Warn("Error reading initial websocket message: ", err)
	}

	// create a struct to put the parsed message json into
	message := WebsocketMessage{}

	// put the received message content into our object
	err = json.Unmarshal(messageBytes, &message)

	// create a struct containing the message we will send back
	// we will fill this with the data that was requested
	response := WebsocketMessage{
		Content: make(map[string]json.RawMessage),
		Source: containerToId["main_data_consumer"],
		Destination: message.Source,
	}

	// flag that tracks whether or not the received message is valid
	isValid := true
	responseContent := make(map[string]interface{})
	// iterate through each field of the received message 'Content', this is a container's way of requesting specific information
	// we will send back a message with identical keys containing the requested data
	for key, jsonVal := range message.Content {
		var val interface{}
		json.Unmarshal(jsonVal, &val)
		// consider each type of data request that a message could contain
		// these are standardized across containers
		switch key {
		case "coins":
			// 'val' doesn't matter here, simply return the data consumer's internal list of coins
			responseContent[key] = dc.Coins
		case "candles":
			// val -> number of previous minutes of candle data to send
			responseContent[key] = dc.GetCandleData(int64(val.(float64)))
		case "trade_profits":
			// val -> maximum number of previous trade profits to send per coin
			responseContent[key] = dc.GetTradeProfits(int64(val.(float64)))
		case "open_trades":
			// 'val' doesn't matter, here return the components (Entries, Partial Exits) of all open trades
			responseContent[key] = dc.GetOpenTrades()
		case "balance_history":
			// val -> maximum number of previous portfolio balances to return 
			responseContent[key] = dc.GetBalanceHistory(int64(val.(float64)))
		default:
			// the default case means that this key is not a recognized type of data request
			// meaning the received message was not valid
			isValid = false
			log.Warn("Unrecognized initialization data request type: ", key, ". No action will be taken for this field.")
		}
	}
	response.Content = *InterfaceToRawJSON(&responseContent)
	dc.Clients[idToContainer[message.Source]] = &Client{}
	// store the client connection for the container that has connected
	dc.Clients[idToContainer[message.Source]].SetClient(websocket, message.Source)
	if isValid {
		// send the response to the client
		go dc.Clients[idToContainer[message.Source]].WriteMessage(&response, nil)
	}
	

}

/*
	ARGS:
        -> N/A
    RETURN:
        -> N/A
    WHAT:
		-> Waits until it has 3 connections and gets a start message from beverly hills so it can start consuming
*/
func (dc *DataConsumer) WaitForAllConnections() {
	for len(dc.Clients) < 3{
		time.Sleep(1 * time.Second)
	}
	log.Println("Waiting for 'ready' messages from clients...")
	for _, client := range dc.Clients {
		client.AwaitReadyMsg()
		dc.ConnectionsReady++
	}
	log.Println("Received 'ready' messages from clients")
}

/*
	ARGS:
        -> N/A
    RETURN:
        -> N/A
    WHAT:
		-> Wrapper for consuming the data
*/
func (dc *DataConsumer) StartConsumption() {
	log.Println("Started Consumption")

	symbolsUSD := []string{}
	for _, sym := range *dc.Coins {
		symbolsUSD = append(symbolsUSD, strings.ToUpper(sym)+"-USD")
	}
	for {
		log.Println("Starting initialization for coins: " + strings.Join(*dc.Coins, ", "))
		coinbaseSocket, err := InitCoinbaseWebsocket(&symbolsUSD)
		for err != nil {
			log.Warn("Was not able to open symbol websocket with error: " + err.Error())
			time.Sleep(1 * time.Second)
			log.Warn("Trying to reconnect...")
			coinbaseSocket, err = InitCoinbaseWebsocket(&symbolsUSD)
			
		}
		log.Println("Connected to Coinbase")
		dc.ConsumeData(coinbaseSocket)
	}
}


/*
	ARGS:
        -> conn (*ws.Conn): pointer to the exchange websocket connection
    RETURN:
        -> N/A
    WHAT:
		-> The loop that consumes the data from the websocket
*/
func (data *DataConsumer) ConsumeData(conn *ws.Conn) {
	for {
		message := CoinbaseMessage{}
		if err := conn.ReadJSON(&message); err != nil {
			log.Warn("Was not able to retrieve message with error: " + err.Error())
			conn.Close()
			log.Warn("Attempting to restart connection...")
			return
		}
		if message.Type != "subscriptions" {
			data.ProcessTick(&message)
		}
	}
}

/*
	ARGS:
        -> msg (*CoinBaseMessage): message from coin base
    RETURN:
        -> N/A
    WHAT:
		-> Function to process each tick. Sending to containers and also saving in db
		-> Also computing the caandles for each coin each minute
	TODO:
		-> Seperate into more functions
*/
func (dc *DataConsumer) ProcessTick(msg *CoinbaseMessage) {
	tradePrice, _ := strconv.ParseFloat(msg.Price, 64)
	volume, _ := strconv.ParseFloat(msg.LastSize, 64)
	//send data to the frontend
	coinInMessage := strings.Split(msg.ProductID, "-")[0]
	now := int64(msg.Time.Unix())
	now_minute := now / 60
	msgContent := make(map[string]interface{})
	msgContent["price"] = CoinPrice{
		Coin:  coinInMessage,
		Price: tradePrice,
		Time:  now,
	}
	
	messageToFrontend := &WebsocketMessage{
		Content: *InterfaceToRawJSON(&msgContent),
		Source: containerToId["main_data_consumer"],
		Destination: containerToId["frontend"],
	}

	frontendClient := dc.Clients["frontend"]
	if dc.ConnectionsReady == 3 {
		go frontendClient.WriteMessage(messageToFrontend, nil)
	}
	
	candle := dc.Candlesticks[coinInMessage]
	candle_min := int64(0)
	if candle != nil {
		candle_min = candle.Timestamp / 60
	}
	if candle == nil {
		dc.Candlesticks[coinInMessage] = &Candlestick{
			Timestamp: (now / 60) * 60,
			Open:      tradePrice,
			High:      tradePrice,
			Low:       tradePrice,
			Close:     tradePrice,
			Volume:    volume,
			Trades: 1,
		}
	} else if candle_min != now_minute {
		newCandle := &Candlestick{
			Timestamp: (now / 60) * 60,
			Open:      tradePrice,
			High:      tradePrice,
			Low:       tradePrice,
			Close:     tradePrice,
			Volume:    volume,
			Trades: 1,
		}
		wg := new(sync.WaitGroup)
		if dc.ConnectionsReady == 3 {
			wg.Add(2)
			candlesToSend := make(map[string][]Candlestick)
			if dc.CandlesInQueue {
				for _, coin := range *dc.Coins {
					candlesToSend[coin] = dc.CandlesticksQueue[coin]
					dc.CandlesticksQueue[coin] = []Candlestick{}
				}
				dc.CandlesInQueue = false
			}
			for _, coin := range *dc.Coins {
				candlesToSend[coin] = append(candlesToSend[coin], *dc.Candlesticks[coin])
			}
			msgContent := make(map[string]interface{})
			msgContent["candles"] = candlesToSend
			for destinationStr, client := range dc.Clients {
				if destinationStr != "frontend" {
					candleMessage := WebsocketMessage{
						Source:      containerToId["main_data_consumer"],
						Destination: containerToId[destinationStr],
						Content:     *InterfaceToRawJSON(&msgContent),
					}
					go client.WriteMessage(&candleMessage, wg)
				}
			}
		} else {
			if !dc.CandlesInQueue {
				// do any smoothing that needs to occur
				smoothedCandles := SmoothBetweenCandles(candle, newCandle)
				dc.CandlesticksQueue[coinInMessage] = *smoothedCandles
				dc.CandlesInQueue = true
			}
			dc.CandlesticksQueue[coinInMessage] = append(dc.CandlesticksQueue[coinInMessage], *newCandle)
		}
		
		
		//store in db
		dc.StoreCandles(&dc.Candlesticks)

		wg.Wait()

		dc.Candlesticks[coinInMessage] = newCandle
		for _, coin := range *dc.Coins {
			dc.Candlesticks[coin] = &Candlestick{
				Timestamp: (now / 60) * 60,
				Open:      dc.Candlesticks[coin].Close,
				High:      dc.Candlesticks[coin].Close,
				Low:       dc.Candlesticks[coin].Close,
				Close:     dc.Candlesticks[coin].Close,
				Volume:    volume,
				Trades: 1,
			}
		}
	} else {
		candle.Close = tradePrice
		candle.High = math.Max(candle.High, tradePrice)
		candle.Low = math.Min(candle.Low, tradePrice)
		candle.Trades++
		candle.Volume += volume
	}
	return
}

/*
	ARGS:
        -> symbols (*[]string): pointer to slice of symbols we are subbing to
    RETURN:
		-> (*ws.Conn): a pointer to the exchange websocket connection
		-> (error): error if we can't write to the
    WHAT:
		-> Initializes the coinbase socket by subscribing to the correct channels
*/
func InitCoinbaseWebsocket(symbols *[]string) (*ws.Conn, error) {
	wsConn, _, err := wsDialer.Dial("wss://ws-feed.pro.coinbase.com", nil)
	if err != nil {
		return nil, err
	}
	subscribe := CoinbaseMessage{
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

