package main

import (
	//"alert"

	"time"

	"github.com/ross-hugo/go-binance/v2"
)

func main() {
	time.Sleep(5 * time.Second)
	binanceClinet = *binance.NewClient(apiKey, secretKey)
	// TODO: get coins from data consumer :)
	coins = [3]string{"ETH", "DOGE", "LTC"}
	strategy := initAtlas(coins)

	// go userDataStream()
	//connect to data consumer
	// startServer()
	startClient()
	startPM()

}
