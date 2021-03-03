package main

//"alert"

func main() {

	pm := initPM()
	go pm.StartServer()
	initialized := make(chan bool, 1)
	go pm.ReadOrderBook(initialized)
	<-initialized
	pm.StartTrading()
}
