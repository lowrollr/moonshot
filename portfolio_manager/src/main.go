package main

import (
	//"alert"

	"time"

	"github.com/ross-hugo/go-binance/v2"
)

func main() {
	time.Sleep(5 * time.Second)
	binanceClinet = *binance.NewClient(apiKey, secretKey)
	// go userDataStream()
	//connect to data consumer
	// startServer()
	startClient()
}
