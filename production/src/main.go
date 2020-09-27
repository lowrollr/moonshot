package main

import (
	//"alert"
	"fmt"
 )

func main() {
	fmt.Println("Connectting to database")
	//Here going to connect to database
	var err error = nil

	global_db, err = Dumbo.connectDB(db_string)
	if err != nil {
		panic(err)
	}
	fmt.Println("Connected to database successfully")

	fmt.Println("Creating tables in database")
	err = Dumbo.autoMigrate(global_db)
	if err != nil {
		panic(err)
	}
}
