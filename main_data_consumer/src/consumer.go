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
	"strings"
	"time"

	"github.com/adshao/go-binance/v2"
)

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
	partition_nano := time.Minute.Nanoseconds() / int64(partition)
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
	fmt.Println("There error encountered " + err.Error())
	fmt.Println(err)
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
		time.Sleep(24 * time.Hour)
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
	the_time := time.Now()
	if the_time.Minute()%3 == 2 {
		binance.WebsocketKeepalive = true
	} else if the_time.Minute()%3 == 1 {
		binance.WebsocketKeepalive = false
	}
	times_per_min := 3

	now := time.Now()
	fmt.Println(event)
	// store the event in database
	err := Dumbo.StoreCryptoBidAsk(event)
	if err != nil {
		fmt.Println("Was not able to store crypto information " + err.Error())
		panic(err)
	}
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
	the_time := time.Now()
	if the_time.Minute()%3 == 2 {
		binance.WebsocketKeepalive = true
	} else if the_time.Minute()%3 == 1 {
		binance.WebsocketKeepalive = false
	}
	//Time to wait: 1 / 1 minute
	times_per_min := 1

	now := time.Now()
	fmt.Println(event)
	// store the event in database
	err := Dumbo.StoreCryptoKline(event)
	if err != nil {
		fmt.Println("Was not able to store crypto information " + err.Error())
		panic(err)
	}
	// sleep to get maximum efficiency from socket
	EfficientSleep(times_per_min, now, time.Minute)
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
		stop_order_chan, _, err := binance.WsPartialDepthServe(symbol, depth, tradeOrderDataConsumer, ErrorTradeHandler)
		if err != nil {
			panic(err)
		}
		<-stop_order_chan
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
		stop_candle_chan, _, err := binance.WsKlineServe(symbol, kline_interval, tradeKlineDataConsumer, ErrorTradeHandler)
		if err != nil {
			panic(err)
		}
		<-stop_candle_chan
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

	kline_interval := "1m"
	order_book_depth := "20"

	fmt.Println("Starting consuming...")

	for _, symbol := range *coins {
		//Using quote currency as tether to open socket to binance
		symbol = strings.ToLower(symbol) + "usdt"
		go OrderBookGoRoutine(symbol, order_book_depth)
		go KlineGoRoutine(symbol, kline_interval)
	}

	//perpetual wait
	waitFunc()
}
