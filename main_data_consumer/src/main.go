/*
FILE: main.go
AUTHORS:
    -> Ross Copeland <rhcopeland101@gmail.com>
	-> Jacob Marshall <marshingjay@gmail.com>
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
*/
func main() {

	// Initialize the Data Consumer
	dataConsumer := InitDataConsumer()

	// Initialize tables in the database
	dataConsumer.InitializeDB()

	// listen for client connections
	go dataConsumer.WsHTTPListen()

	// listen for 'ready' messages
	go dataConsumer.WaitForAllConnections()

	// Start consuming data
	dataConsumer.StartConsumption()
}
