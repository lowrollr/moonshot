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
	"errors"
	"fmt"
	"strings"
	"time"

	"github.com/adshao/go-binance"
)

/*
	ARGS:
		-> partition (int): < 5. how many times per second you want to receive data
			-> binance does not allow for larger than 5
		-> prev_time (time.Time) at what time data was received to compute how long to wait
    RETURN:
        -> N/A
    WHAT: 
		-> Waits the partition time but only that long and no longer
		-> Makes sure it does not wait less than partition so that IP is not blocked from binance
		-> Partition time is part of one second ex: 1/2 secoond, 1/3 second etc.
*/
func EfficientSleep(partition int, prev_time time.Time) {
	if partition > 5 {
		panic(errors.New("Must not be longer than 5 or will get rate limited"))
	}
	prev_time_nano := int64(prev_time.Nanosecond())
	later_nano := int64(time.Now().Nanosecond())
	partition_nano := time.Second.Nanoseconds() / int64(partition)
	if later_nano-prev_time_nano > 0 {
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
	fmt.Println("Was an error " + err.Error())
	panic(err)
}

/*
	ARGS:
		-> stops ([]chan struct{}): slice of channels to stop the socket
		-> kills ([]chan struct{}): slice of channels to kill the socket
    RETURN:
        -> N/A
    WHAT: 
		-> Needs some goroutine to constantly be doing something, hence the busy loop here
    TODO:
		-> the channel slices aren't really doing anything here, figure out better
			way to handle errors or failure to gracefully exit say and then deal with 
			channel slices
*/
func waitFunc(stops, kills []chan struct{}) {
	fmt.Println("entered the wait func")
	for true {
		time.Sleep(1 * time.Minute)
	}
	for _, c := range stops {
		c <- struct{}{}
	}
	for _, c := range kills {
		c <- struct{}{}
	}
}

/*
	ARGS:
        -> N/A
    RETURN:
        -> N/A
    WHAT: 
		-> Consumes data and stores in the DB
		-> Uses binance web socket to obtain data and send to db
*/
func ConsumeData() {
	binance.WebsocketKeepalive = true
	tradeDataConsumer := func(event *binance.WsTradeEvent) {
		fmt.Println("Entered the trade consume to store data")
		now := time.Now()
		fmt.Println(event)
		// store the event in database
		err := Dumbo.StoreCrypto(*event)
		if err != nil {
			fmt.Println("Was not able to store crypto information " + err.Error())
			panic(err)
		}
		// sleep to get maximum efficiency
		EfficientSleep(1, now)
	}

	symbols := []string{"BTC", "ETH", "XRP", "LTC", "BCH", "LINK", "BNB", "ADA", "DOT", "XMR"}
	fmt.Println("Starting consuming...")

	stops := []chan struct{}{}
	kills := []chan struct{}{}

	for _, symbol := range symbols {
		symbol = strings.ToUpper(symbol) + "USDT"
		stop_chan, kill_chan, err := binance.WsTradeServe(symbol, tradeDataConsumer, ErrorTradeHandler)
		if err != nil {
			fmt.Println(err)
			panic(err)
		}
		stops = append(stops, stop_chan)
		kills = append(kills, kill_chan)
	}
	waitFunc(stops, kills)
}
