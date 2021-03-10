/*
FILE: pm.go
AUTHORS:
	-> Ross Copeland <rhcopeland101@gmail.com>
	-> Jacob Marshall <marshingjay@gmail.com>

WHAT:
	-> main entry point for PM execution
*/

package main

/*
	ARGS:
		-> N/A
    RETURN:
        -> N/A
    WHAT:
		-> initializes PM container and starts operation
*/
func main() {
	// initialize dumbo (database) object
	Dumbo = &dumbo{}

	// initialize Portfolio Manager
	pm := initPM()

	// start PM server
	go pm.StartServer()

	// create initialized channel (we need to wait until order books are initialized before calling startTrading)
	initialized := make(chan bool, 1)

	// create order book routine
	go pm.ReadOrderBook(initialized)

	// wait for initialized channel to be set to true
	<-initialized

	// start trading procedures
	pm.StartTrading()
}
