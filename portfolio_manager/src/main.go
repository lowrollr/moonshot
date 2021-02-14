package main

//"alert"

func main() {
	// binanceClinet := *binance.NewClient(apiKey, secretKey)

	pm := initPM()
	atlas := initAtlas(pm.Coins)
	pm.SetStrategy(atlas)

	pm.FrontendSocket = startServer()
	pm.StartTrading()

	// _ = initAtlas(&coins)

	// go userDataStream()
	//connect to data consumer
	//

	// startPM()

}
