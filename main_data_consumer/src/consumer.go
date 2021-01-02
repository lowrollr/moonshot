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
func EfficientSleep(partition int, prev_time time.Time) {
	// if partition > 5 || partition <= 0{
	// 	panic(errors.New("Must be between 0 and 5 for partition or will get rate limited"))
	// }

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
		-> stops ([]chan struct{}): slice of channels to stop the socket
    RETURN:
        -> N/A
    WHAT:
		-> Needs some goroutine to constantly be doing something, hence the busy loop here
*/
func waitFunc(stops []chan struct{}) {
	time.Sleep(23 * time.Hour)
	for _, c := range stops {
		c <- struct{}{}
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
	EfficientSleep(times_per_min, now)
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
		fmt.Println("ASLDKFJSALKDJFLASKJDVLQIWJFLASDLIASJFLDJKASLKF")
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
	EfficientSleep(times_per_min, now)
}

/*
	ARGS:
        -> coins (*[]string) pointer to slice of strings of abrvs of coins
    RETURN:
        -> N/A
    WHAT:
		-> Consumes data and stores in the DB
		-> Uses binance web socket to obtain data and send to db
	TODO:
		-> Change so that it gets coin abreviations from database
		-> Is tether the best coin to transfer to?
		-> Figure out better way to determine stable coins other than manually
*/
func ConsumeData(coins *[]string) {
	//want to check if the socket is still connected to if we are running > 24 hrs
	// binance.WebsocketKeepalive = true
	binance.WebsocketTimeout = time.Minute * 3

	kline_interval := "1m"
	order_book_depth := "10"

	fmt.Println("Starting consuming...")

	stops := []chan struct{}{}

	for {
		for _, symbol := range *coins {
			//Using quote currency as tether to open socket to binance
			symbol = strings.ToLower(symbol) + "usdt"
			stop_order_chan, _, err := binance.WsPartialDepthServe(symbol, order_book_depth, tradeOrderDataConsumer, ErrorTradeHandler)
			stop_candle_chan, _, err := binance.WsKlineServe(symbol, kline_interval, tradeKlineDataConsumer, ErrorTradeHandler)

			time.Sleep(1 * time.Second)

			if err != nil {
				fmt.Println(err)
				panic(err)
			}

			stops = append(stops, stop_order_chan)
			stops = append(stops, stop_candle_chan)
		}

		//perpetual wait
		waitFunc(stops)
	}
}
