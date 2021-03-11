/*
FILE: data_consumer.go
AUTHORS:
	-> Ross Copeland <rhcopeland101@gmail.com>
	-> Jacob Marshall <marshingjay@gmail.com>
WHAT:
	-> This containers most main functions for the data consumer
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
	NumConnections int
	SmoothPastVals bool
}

/*
	ARGS:
        -> N/A
    RETURN:
        -> a DataConsumer pointer
    WHAT:
		-> Creates a dataconsumer object
		-> Initializes the clinet objects and NumConnections
*/
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
		SmoothPastVals: false,
	}
}

/*
	ARGS:
        -> N/A
    RETURN:
        -> N/A
    WHAT:
		-> Does all the DB setup needed, getting the coins and initializing tables
*/
func (data *DataConsumer) DBSetUp() {
	data.Coins = Dumbo.SelectCoins(-1)
	Dumbo.InitializeDB()
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
func (data *DataConsumer) WsHTTPListen() {
	http.HandleFunc("/", data.handleConnections)
	err := http.ListenAndServe(":"+string(os.Getenv("SERVERPORT")), nil)
	if err != nil {
		log.Fatal("ListenAndServe: ", err)
	}
}

/*
	ARGS:
        -> N/A
    RETURN:
        -> N/A
    WHAT:
		-> Handling of the connection, whether it be coins, reconnect etc.
	TODO:
		-> change to switch statement with different functions
*/
func (data *DataConsumer) handleConnections(w http.ResponseWriter, r *http.Request) {
	ws, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		log.Warn("error", err)
	}
	message := SocketMessage{}
	_, messagae_bytes, err := ws.ReadMessage()
	if err != nil {
		log.Warn("error", err)
	}
	err = json.Unmarshal(messagae_bytes, &message)
	if err != nil {
		log.Warn("Was not able to unmarshall", err)
	}

	if message.Type == "coins" {
		data.Clients[idToContainer[message.Source]].SetClient(ws, message.Source)
		coinMessage := SocketCoinMessageConstruct(
			data.Coins,
			containerToId["main_data_consumer"],
			message.Source,
		)
		data.Clients[idToContainer[message.Source]].
			WriteSocketCoinsJSON(coinMessage)
	} else if message.Type == "reconnect" {
		data.Clients[idToContainer[message.Source]].SetClient(ws, message.Source)
		log.Println("Reconnected to ", idToContainer[message.Source], ws.RemoteAddr())
	} else if message.Type == "pm_data" {
		data.Clients[idToContainer[message.Source]].SetClient(ws, message.Source)
		if message.Msg == "" {
			log.Warn("Did not send number of max entries to retrieve. Error:", err)
		} else {
			all_entries := strings.Split(message.Msg, ",")
			if len(all_entries) == 1 {
				log.Warn("Was not able to get two values for pm data. Entries:", all_entries)
			} else {
				coin_depth, coin_str_err := strconv.Atoi(all_entries[0])
				trade_depth, trade_str_err := strconv.Atoi(all_entries[1])
				if coin_str_err != nil || trade_str_err != nil {
					log.Warn(coin_str_err, trade_str_err)
					var final_err error
					if coin_str_err != nil {
						final_err = coin_str_err
					} else {
						final_err = trade_str_err
					}
					errMessage := SocketPMDataConstruct(
						&TradesAndCandles{},
						containerToId["main_data_consumer"],
						message.Source,
						final_err.Error(),
					)
					data.Clients[idToContainer[message.Source]].WriteSocketPMDataJSON(errMessage)
				} else {
					trades_candles, smooth_next_vals := Dumbo.GetAllPMData(data.Coins, coin_depth, trade_depth)
					data.SmoothPastVals = smooth_next_vals
					dataMessage := SocketPMDataConstruct(
						trades_candles,
						containerToId["main_data_consumer"],
						message.Source,
						"nil",
					)
					data.Clients[idToContainer[message.Source]].WriteSocketPMDataJSON(dataMessage)
				}
			}
		}
	} else if message.Type == "data" {
		data.Clients[idToContainer[message.Source]].SetClient(ws, message.Source)
		if message.Msg == "" {
			log.Warn("Did not send number of max entries to retrieve. Error:", err)
		} else {
			entries, err := strconv.Atoi(message.Msg)
			if err != nil {
				log.Warn("Was not able to convert string to num. Send correct entry num. Error:", err)
			} else {
				all_coin_candle, bool_smooth_next_vals := Dumbo.GetAllPreviousCandles(data.Coins, entries)
				data.SmoothPastVals = bool_smooth_next_vals
				dataMessage := SocketAllCandleConstruct(
					all_coin_candle,
					containerToId["main_data_consumer"],
					message.Source,
				)
				data.Clients[idToContainer[message.Source]].WriteSocketAllDataJSON(dataMessage)
			}
		}
	} else {
		log.Warn("Did not provide correct type. Message received:", message)
	}
	data.NumConnections++
	return
}

/*
	ARGS:
        -> N/A
    RETURN:
        -> N/A
    WHAT:
		-> Waits until it has 3 connections and gets a start message from beverly hills so it can start consuming
*/
func (data *DataConsumer) ServerListen() {
	for {
		if data.NumConnections > 2 {
			break
		}
		time.Sleep(1 * time.Second)
	}
	data.Clients["beverly_hills"].WaitStart()
}

/*
	ARGS:
        -> N/A
    RETURN:
        -> N/A
    WHAT:
		-> Wrapper for consuming the data
*/
func (data *DataConsumer) StartConsume() {
	InitConsume()
	data.Consume()
}

/*
	ARGS:
        -> N/A
    RETURN:
        -> N/A
    WHAT:
		-> Main function for consuming the data from exchange. Adds -USD to the end
*/
func (data *DataConsumer) Consume() {
	data.Candlesticks = make(map[string]*Candlestick)
	log.Println("Start Consuming")

	symbolsUSD := []string{}
	for _, sym := range *data.Coins {
		symbolsUSD = append(symbolsUSD, strings.ToUpper(sym)+"-USD")
	}
	data.SymbolWebSocket(&symbolsUSD)
}

/*
	ARGS:
        -> symbols (*[]string): pointer to slice of the symbols we are using in coinbase
    RETURN:
        -> N/A
    WHAT:
		-> Uses symbols to start the consumption
*/
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

/*
	ARGS:
        -> conn (*ws.Conn): pointer to the exchange websocket connection
		-> symbols (*[]string): pointer to slice of the symbols we are using in coinbase
    RETURN:
        -> N/A
    WHAT:
		-> The loop that consumes the data from the websocket
*/
func (data *DataConsumer) ConsumeData(conn *ws.Conn, symbols *[]string) {
	// sec := 60 - time.Now().Second()
	// if sec != 60 {
	// 	log.Println("Waiting", sec, "second(s) to top of minute...")
	// 	time.Sleep(time.Duration(sec) * time.Second)
	// }

	for {
		message := CoinBaseMessage{}
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
func (data *DataConsumer) ProcessTick(msg *CoinBaseMessage) {
	tradePrice, _ := strconv.ParseFloat(msg.Price, 64)
	volume, _ := strconv.ParseFloat(msg.LastSize, 64)
	//send data to the frontend
	trade_coin := strings.Split(msg.ProductID, "-")[0]
	now := int64(msg.Time.Unix()) / 60

	messageToFrontend := SocketPriceMessageConstruct(
		&CoinPrice{
			Coin:  trade_coin,
			Price: tradePrice,
			Time:  now,
		},
		containerToId["main_data_consumer"],
		containerToId["frontend"],
	)

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
		smoothed_or_orig_candles := data.SmoothIfNeeded()
		for destinationStr, client := range data.Clients {
			if destinationStr != "frontend" {
				candleMessage := SocketAllCandleMessage{
					Source:      containerToId["main_data_consumer"],
					Destination: containerToId[destinationStr],
					Msg:         *smoothed_or_orig_candles,
				}
				// log.Println(candleMessage)
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

func (data *DataConsumer) SmoothIfNeeded() (*map[string][]Candlestick) {
	slice_candles := map[string][]Candlestick{}
	if !data.SmoothPastVals {
		for _, coin := range *(*data).Coins {
			slice_candles[coin] = []Candlestick{*data.Candlesticks[coin]}
		}
		return &slice_candles
	} else {
		//get latest vals
		lastCandles := Dumbo.GetLastCandles(data.Coins)
		for _, coin := range *(*data).Coins {
			num_gaps := int(((*lastCandles)[coin].StartTime - data.Candlesticks[coin].StartTime) / 60)
			
			i :=  0
			gap_slice := make([]Candlestick, num_gaps + 1)
			for j := 1; j < num_gaps; j++ {
				ratio := float64(j)/ float64(num_gaps)
				gap_slice[i] = Candlestick {
					Open: ratio * (data.Candlesticks[coin].Open - (*lastCandles)[coin].Open) + (*lastCandles)[coin].Open,
					High: ratio * (data.Candlesticks[coin].High - (*lastCandles)[coin].High) + (*lastCandles)[coin].High,
					Low: ratio * (data.Candlesticks[coin].Low - (*lastCandles)[coin].Low) + (*lastCandles)[coin].Low,
					Close: ratio * (data.Candlesticks[coin].Close - (*lastCandles)[coin].Close) + (*lastCandles)[coin].Close,
					StartTime: (*lastCandles)[coin].StartTime + int64((j * 60)),
					Volume: (data.Candlesticks[coin].Volume + (*lastCandles)[coin].Volume)/2,
					NumTrades: (data.Candlesticks[coin].NumTrades + (*lastCandles)[coin].NumTrades)/2,
					coinName: (*lastCandles)[coin].coinName,
				}
			}
			gap_slice[0] = (*lastCandles)[coin]
			gap_slice[num_gaps] = *data.Candlesticks[coin]
			slice_candles[coin] = gap_slice
		}
		data.SmoothPastVals = false
		return &slice_candles
	}
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

/*
	ARGS:
        -> N/A
    RETURN:
        -> N/A
    WHAT:
		-> Things to run right before consuming
		-> Setting up the logging config
*/
func InitConsume() {
	log.SetFormatter(&log.TextFormatter{ForceColors: true, FullTimestamp: true})
}
