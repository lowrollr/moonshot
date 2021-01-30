package main

import (
	//"alert"

	"time"
)

func main() {
	time.Sleep(5 * time.Second)
	// binanceClinet := *binance.NewClient(apiKey, secretKey)

	pm := initPM(100.0)
	atlas := initAtlas(pm.coins)
	pm.SetStrategy(atlas)

	// _ = initAtlas(&coins)

	// go userDataStream()
	//connect to data consumer
	// startServer()
	startClient()
	// startPM()

}
