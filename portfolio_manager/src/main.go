package main

//"alert"

func main() {

	pm := initPM()
	go pm.StartServer()
	initialized := make(chan bool, 1)
	go pm.ReadOrderBook(initialized)
	<-initialized
	pm.StartTrading()

	// _ = initAtlas(&coins)

	// go userDataStream()
	//connect to data consumer
	//

	// startPM()

}
