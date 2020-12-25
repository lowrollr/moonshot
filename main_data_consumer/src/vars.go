/*
FILE: vars.go
AUTHORS:
    -> Ross Copeland <rhcopeland101@gmail.com>
WHAT:
	-> Global variables needed for programs
	-> Right now it is just variables needed for connecting and 
		interfacing with the database
*/
package main

import (
	"os"

	"github.com/jinzhu/gorm"
)

var (
	dbType    = os.Getenv("DBTYPE")
	db_string = os.Getenv("DBTYPEURL") + "://" + os.Getenv("DBUSER") + ":" + os.Getenv("DBPASS") + "@" + os.Getenv("DBNETLOC") + ":" + os.Getenv("DBPORT") + "/" + os.Getenv("DBNAME") + "?sslmode=disable"
	
	scrape_url = "https://coinmarketcap.com/all/views/all/"
	
	Dumbo = &dumbo{}
	global_db *gorm.DB
)