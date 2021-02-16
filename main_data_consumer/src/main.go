/*
FILE: main.go
AUTHORS:
    -> Ross Copeland <rhcopeland101@gmail.com>
WHAT:
	-> Entry point for the main consumer container
	-> This will collect all information on coins (price, volume, time)
*/
package main

/*
	ARGS:
        -> N/A
    RETURN:
        -> N/A
    WHAT:
		-> Connects to DB, creates tables if there aren't
		-> Consumes data and stores in the DB
    TODO:
        -> General review of this code since it is pretty critical
*/
func main() {
	Dumbo = &dumbo{}
	dataConsumer := initDC()
	dataConsumer.DBSetUp()
	go dataConsumer.WsHTTPListen()

	dataConsumer.ServerListen()

	dataConsumer.StartConsume()
}
