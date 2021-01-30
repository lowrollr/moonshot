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

type HistoricalCrypto struct {
	gorm.Model
	CoinAbv    string  `gorm:"Type:varchar(7);not null;"`
	Price     float32 `gorm:"Type:NUMERIC(8,2);not null;"`
	Timestamp int64   `gorm: "Type:timestamp with time zone default now();"`
	//Volume    int64   `gorm:"not null"`
}

type CurrentCryptoPrice struct {
	gorm.Model
	CoinAbv    string  `gorm:"Type:varchar(7);not null;unique;primary key;"`
	Price     float32 `gorm:"Type:NUMERIC(8,2);not null;"`
	Timestamp int64   `gorm: "Type:timestamp with time zone default now();"`
}

type CryptoNames struct {
	CoinAbv string `gorm:"Type:varchar(7);not null;unique;primary key"`
	CoinName   string `gorm:"Type:varchar(50); not null;"`
}