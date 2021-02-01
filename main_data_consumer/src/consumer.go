/*
FILE: consumer.go
AUTHORS:
    -> Ross Copeland <rhcopeland101@gmail.com>
WHAT:
	-> Code for actual consumption of data from bianance
	-> This will collect all information on coins (price, volume, time)
*/
package main

import (
	"fmt"
	"math"
	"strconv"
	"strings"
	"time"
	"os/exec"

	"github.com/ross-hugo/go-binance/v2"
	log "github.com/sirupsen/logrus"
)

func printNumSockets() {
	command := "netstat -penut | grep ESTABLISHED | wc -l"
	out, err := exec.Command("sh", "-c", command).Output()
	if err != nil {
		panic(err)
	}
	// netstat_out, _ := exec.Command("netstat -penut").Output()
	// log.Println("testing netstat: " + strings.TrimSpace(string(netstat_out)))
	log.Println("\n\nNumber of sockets in use: " + strings.TrimSpace(string(out)))
}

/*
	ARGS:
		-> partition (int): < 5. how many times per minute you want to receive data
			-> binance does not allow for larger than 5
		-> prev_time (time.Time) at what time data was received to compute how long to wait
    RETURN:
        -> N/A
    WHAT:
		-> Waits the partition time but only that long and no longer
		-> Makes sure it does not wait less than partition so that IP is not blocked from binance
		-> Partition time is part of one second ex: 1/2 minute, 1/3 minute etc.
*/
func EfficientSleep(partition int, prev_time time.Time, duration time.Duration) {
	prev_time_nano := int64(prev_time.UnixNano())
	later_nano := int64(time.Now().UnixNano())
	partition_nano := duration.Nanoseconds() / int64(partition)
	if prev_time_nano-(later_nano-prev_time_nano) > 0 {
		time.Sleep(time.Duration(partition_nano-(later_nano-prev_time_nano)) * time.Nanosecond)
	}
}

/*
	ARGS:
        -> err (error) the error that was received
    RETURN:
        -> N/A
    WHAT:
		-> Function used in other functions to determine how errors should be handled
		-> ATM it is just panicing
    TODO:
		-> Should have a better way to deal with errors, some sort of logging,
			diagnostic, restart service, etc
*/
func ErrorTradeHandler(err error) {
	log.Warn("There error encountered " + err.Error())
	log.Warn(err)
}

/*
	ARGS:
		-> N/A
	RETURN:
        -> N/A
    WHAT:
		-> Needs some goroutine to constantly be doing something, hence the busy loop here
*/
func waitFunc() {
	for {
		time.Sleep(10 * time.Second)
		printNumSockets()
	}
}

/*
	ARGS:
		-> event (*binance.WsPartialDepthEvent):
    RETURN:
        -> N/A
    WHAT:
		-> Function passed into binance websocket function on how to handle received orderbook data
		-> Passes data to the database storing function
*/
var tradeOrderDataConsumer func(event *binance.WsPartialDepthEvent) = func(event *binance.WsPartialDepthEvent) {
	now := time.Now()
	if now.Minute()%3 == 2 {
		binance.WebsocketKeepalive = true
	} else if now.Minute()%3 == 1 {
		binance.WebsocketKeepalive = false
	}
	times_per_min := 3
	// store the event in database
	
	// err := Dumbo.StoreCryptoBidAsk(event)
	// if err != nil {
	// 	log.Warn("Was not able to store order data with error:" + err.Error())
	// 	printNumSockets()
	// }
	// sleep to get maximum efficiency from socket
	EfficientSleep(times_per_min, now, time.Minute)
}

/*
	ARGS:
		-> event (*binance.WsKlineEvent): pointer to kline candlestick data
    RETURN:
        -> N/A
    WHAT:
		-> Function passed into binance websocket function on how to handle received candlestick data
		-> Passes data to the database storing function
*/
var tradeKlineDataConsumer func(*binance.WsKlineEvent) = func(event *binance.WsKlineEvent) {
	now := time.Now()
	//Time to wait: 1 / 1 minute
	times_per_min := 1
	// store the event in database
	
	err := Dumbo.StoreCryptoKline(event)
	if err != nil {
		log.Warn("Was not able to store kline data with error: " + err.Error())
		printNumSockets()
	}
	// sleep to get maximum efficiency from socket
	EfficientSleep(times_per_min, now, time.Minute)
}

/*
	ARGS:
		-> event (*binance.WsTradeEvent): pointer to kline candlestick data
    RETURN:
        -> N/A
    WHAT:
		-> Function passed into binance websocket function on how to handle received candlestick data
		-> Passes data to the database storing function
	TODO:
		-> initialize and sleep at the same time so not wasting time, use channels
*/
var singularTradeDataConsumer func(*binance.WsTradeEvent) = func(event *binance.WsTradeEvent) {
	//toggle for the ping/pong
	times_per_duration := 4
	now := time.Now()
	if now.Minute()%3 == 2 {
		binance.WebsocketKeepalive = true
	} else if now.Minute()%3 == 1 {
		binance.WebsocketKeepalive = false
	}
	volume, err1 := strconv.ParseFloat(event.Quantity, 32)
	curPrice, err2 := strconv.ParseFloat(event.Price, 32)
	symbol := strings.Split(strings.ToLower(event.Symbol), "usdt")[0]

	if err1 != nil || err2 != nil {
		log.Warn(err1.Error() + err2.Error())
	}

	if err1 == nil && err2 == nil {
		if shortCandleStickData[symbol].StartTime == 0 {
			shortCandleStickData[symbol].StartTime = event.Time
		}
		if shortCandleStickData[symbol].Open == 0 {
			shortCandleStickData[symbol].Open = float32(curPrice)
		}

		shortCandleStickData[symbol].EndTime = event.Time
		shortCandleStickData[symbol].Close = float32(curPrice)

		shortCandleStickData[symbol].High = Float32Max(shortCandleStickData[symbol].High, float32(curPrice))
		shortCandleStickData[symbol].Low = Float32Min(shortCandleStickData[symbol].Close, float32(curPrice))

		shortCandleStickData[symbol].Volume += float32(volume)

		if now.Second()%20 == 0 {
			// err := Dumbo.StoreCryptosCandle(shortCandleStickData)
			// if err != nil {
			// 	log.Warn("Was not able to store crypto information " + err.Error())
			// 	log.Warn(shortCandleStickData)
			// }
		}
	}
	ZeroShortCandleStick(symbol)
	// sleep to get maximum efficiency from socket
	EfficientSleep(times_per_duration, now, time.Second)
}

/*
	ARGS:
		-> symbol (string): string of the symbol ex: btcusdt
		-> depth (string): string of how deep to look in the order book ex: 20
    RETURN:
        -> N/A
    WHAT:
		-> funciton for goroutine for getting the order book data
		-> Uses binance web socket to obtain data and send to db
*/
func OrderBookGoRoutine(symbol string, depth string) {
	for {
		log.Println("Starting goroutine for getting the order book data from coin: " + symbol)
		stop_order_chan, _, err := binance.WsPartialDepthServe(symbol, depth, tradeOrderDataConsumer, ErrorTradeHandler)
		if err != nil {
			// panic(err)
			log.Warn("Was not able to open websocket to the orderbook data with error: " + err.Error())
			printNumSockets()
		}
		<-stop_order_chan
		log.Println("Restarting socket for obtaining order book data from coin: " + symbol)
		printNumSockets()
	}
}

/*
	ARGS:
		-> symbol (string): representing the symbol. ex: btcusdt
		-> kline_interval (string): how big a kline to get. ex: 1m
    RETURN:
        -> N/A
    WHAT:
		-> funciton for goroutine for getting the kline candlestick data
		-> Uses binance web socket to obtain data and send to db
*/
func KlineGoRoutine(symbol string, kline_interval string) {
	for {
		log.Println("Starting goroutine for getting the minute kline candlestick data from coin: " + symbol)
		stop_candle_chan, _, err := binance.WsKlineServe(symbol, kline_interval, tradeKlineDataConsumer, ErrorTradeHandler)
		if err != nil {
			// panic(err)
			log.Warn("Was not able to open websocket to the kline data with error: " + err.Error())
			printNumSockets()
		}
		<-stop_candle_chan
		log.Println("Restarting socket for obtaining minute kline data from coin: " + symbol)
		printNumSockets()
	}
}

/*
	ARGS:
		-> symbol (string): representing the symbol. ex: btcusdt
		-> kline_interval (string): how big a kline to get. ex: 1m
    RETURN:
        -> N/A
    WHAT:
		-> funciton for goroutine for getting the kline candlestick data
		-> Uses binance web socket to obtain data and send to db
*/
func TradeGoRoutine(symbol string) {
	for {
		log.Println("Starting goroutine for getting custom kline information from coin: " + symbol)
		stop_candle_chan, _, err := binance.WsTradeServe(symbol, singularTradeDataConsumer, ErrorTradeHandler)
		if err != nil {
			// panic(err)
			log.Warn("Wasa not able to open websocket to the trade data information with error: " + err.Error())
			printNumSockets()
		}
		<-stop_candle_chan
		log.Println("Restarting socket for obtaining custom kline information from coin: " + symbol)
		printNumSockets()
	}
}

/*
	ARGS:
        -> coins (*[]string) pointer to slice of strings of abrvs of coins
    RETURN:
        -> N/A
    WHAT:
		-> Consumes data and stores in the DB
		-> Uses binance web socket to obtain data and send to db
*/
func ConsumeData(coins *[]string) {
	// binance.WebsocketKeepalive = true
	binance.WebsocketTimeout = time.Minute * 3

	fmt.Println(binance.WebsocketTimeout)

	kline_interval := "1m"
	order_book_depth := "20"

	fmt.Println("Starting consuming...")
	log.SetFormatter(&log.TextFormatter{ForceColors: true, FullTimestamp: true})

	for _, symbol := range *coins {
		//Using quote currency as tether to open socket to binance
		symbol = strings.ToLower(symbol) + "usdt"
		go OrderBookGoRoutine(symbol, order_book_depth)
		go KlineGoRoutine(symbol, kline_interval)
		// trade feature not implemented correctly yet
		// go TradeGoRoutine(symbol)
	}
	log.Println("\n\nTotal Number of sockets at the beginning: ")
	printNumSockets()
	//perpetual wait
	waitFunc()
}

func ZeroShortCandleStick(symbol string) {
	shortCandleStickData[strings.ToLower(symbol)] = &OHCLData{}
	shortCandleStickData[strings.ToLower(symbol)].StartTime = 0
	shortCandleStickData[strings.ToLower(symbol)].EndTime = 0
	shortCandleStickData[strings.ToLower(symbol)].Open = 0
	shortCandleStickData[strings.ToLower(symbol)].High = 0
	shortCandleStickData[strings.ToLower(symbol)].Low = math.MaxFloat32
	shortCandleStickData[strings.ToLower(symbol)].Close = 0
	shortCandleStickData[strings.ToLower(symbol)].Volume = 0
}

func InitializeShortCandleStick(coins *[]string) {
	shortCandleStickData = make(map[string]*OHCLData)
	for _, coin := range *coins {
		shortCandleStickData[strings.ToLower(coin)] = &OHCLData{}
		shortCandleStickData[strings.ToLower(coin)].StartTime = 0
		shortCandleStickData[strings.ToLower(coin)].EndTime = 0
		shortCandleStickData[strings.ToLower(coin)].Open = 0
		shortCandleStickData[strings.ToLower(coin)].High = 0
		shortCandleStickData[strings.ToLower(coin)].Low = math.MaxFloat32
		shortCandleStickData[strings.ToLower(coin)].Close = 0
		
		shortCandleStickData[strings.ToLower(coin)].Volume = 0
	}
}
