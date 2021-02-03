package main

import (
	//"alert"

	"time"
)

func main() {
	time.Sleep(8 * time.Second)
	// binanceClinet := *binance.NewClient(apiKey, secretKey)

	pm := initPM(100.0)
	atlas := initAtlas(pm.coins)
	pm.SetStrategy(atlas)

	startServer()
	pm.StartTrading()

	// _ = initAtlas(&coins)

	// go userDataStream()
	//connect to data consumer
	// 

	// startPM()

}
