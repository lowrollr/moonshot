package main

//"alert"

func main() {
	pm := initPM()
	atlas := initAtlas(pm.Coins)
	pm.SetStrategy(atlas)

	go pm.StartServer()
	pm.StartTrading()

	// _ = initAtlas(&coins)

	// go userDataStream()
	//connect to data consumer
	//

	// startPM()

}
