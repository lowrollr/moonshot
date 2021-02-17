package main

//"alert"

func main() {
	// binanceClinet := *binance.NewClient(apiKey, secretKey)

	pm := initPM()

	pm.FrontendSocket = startServer()
	pm.StartTrading()

	// _ = initAtlas(&coins)

	// go userDataStream()
	//connect to data consumer
	//

	// startPM()

}
