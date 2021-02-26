package main

//"alert"

func main() {

	pm := initPM()
	go pm.StartServer()
	// go pm.ReadOrderBook()
	pm.StartTrading()

	// _ = initAtlas(&coins)

	// go userDataStream()
	//connect to data consumer
	//

	// startPM()

}
