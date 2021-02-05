package main

//"alert"

func main() {
	// binanceClinet := *binance.NewClient(apiKey, secretKey)

	pm := initPM(100.0)
	atlas := initAtlas(pm.coins)
	pm.SetStrategy(atlas)

	pm.FrontendSocket = startServer()
	pm.StartTrading()

	// _ = initAtlas(&coins)

	// go userDataStream()
	//connect to data consumer
	//

	// startPM()

}
