/*
FILE: consumer.go
AUTHORS:
    -> Ross Copeland <rhcopeland101.gmail>
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

func ErrorTradeHandler(err error) {
	fmt.Println("Was an error " + err.Error())
	panic(err)
}

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
