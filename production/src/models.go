package main

import (
	"os"
	"github.com/jinzhu/gorm"
)

var (
	db        *gorm.DB
	dbType    = os.Getenv("DBTYPE")
	db_string = os.Getenv("DBTYPE") + "://" + os.Getenv("DBUSER") + ":" + os.Getenv("DBPASS") + "@" + os.Getenv("DBNETLOC") + ":" + os.Getenv("DBPORT") + "/" + os.Getenv("DBNAME") + "?sslmode=disable"
	dbName    = os.Getenv("DBNAME")
)

type Crypto struct {
	gorm.Model
	Symbol    string  `gorm:"Type:varchar(7);not null;"`
	Price     float32 `gorm:"Type:NUMERIC(8,2);not null;"`
	Timestamp int64   `gorm: "Type:timestamp with time zone default now();"`
	Volume    int64   `gorm:"not null"`
}

//add stuff for portfolio manager
