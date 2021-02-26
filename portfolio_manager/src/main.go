package main

//"alert"

func main() {

	pm := initPM()
	go pm.StartServer()

	pm.StartTrading()

	// _ = initAtlas(&coins)

	// go userDataStream()
	//connect to data consumer
	//

	// startPM()

}
