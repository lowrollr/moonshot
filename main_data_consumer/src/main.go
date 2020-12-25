/*
FILE: main.go
AUTHORS:
    -> Ross Copeland <rhcopeland101.gmail>
WHAT:
	-> Entry point for the main consumer container
	-> This will collect all information on coins (price, volume, time)
*/
package main

import (
	"fmt"
)

var (
	Dumbo = &dumbo{}
)
/*
    WHAT: 
		-> Connects to DB, creates tables if there aren't
		-> Consumes data and stores in the DB
    --optional--
    TODO:
        -> General review of this code since it is pretty critical
*/
func main() {
	fmt.Println("Connectting to database")
	//Here going to connect to database
	var err error
	global_db, err = Dumbo.ConnectDB(db_string, dbType)
	if err != nil {
		panic(err)
	}
	fmt.Println("Connected to database successfully")

	fmt.Println("Creating tables in database")
	err = Dumbo.AutoMigrate(global_db)
	if err != nil {
		panic(err)
	}
	fmt.Println("Consuming Data...")
	ConsumeData()
}
