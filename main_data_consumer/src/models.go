/*
FILE: models.go
AUTHORS:
    -> Ross Copeland <rhcopeland101@gmail.com>
WHAT:
	-> Definitions of the tables inside the database
TODO:
	-> Figure out how to do table for each coin with gorm
	-> Better way to store unix timestamp other than bigint
*/
package main

import (
	"github.com/jinzhu/gorm"
)

type OrderBook struct {
	gorm.Model
	BidPrice    float32 `gorm:"Type:real;not null;"`
	BidVolume   float32 `gorm:"Type:real;not null;"`
	AskPrice    float32 `gorm:"Type:real;not null;"`
	AskVolume   float32 `gorm:"Type:real;not null;"`
	Time        int64   `gorm:"type:int;not null"`
	PriorityVal int8    `gorm:"type:not null;"`
	coinName    string  `gorm:"-"`
}

type CoinVolume struct {
	gorm.Model
	Volume   float32 `gorm:"Type:real;not null;"`
	Trades   uint32  `gorm:"not null";`
	coinName string  `gorm:"-"`
	Time     int64   `gorm:"type:int;not null"`
}

// type AllCoinData struct {
// 	gorm.Model
// 	CoinAbv   string  `gorm:"Type:varchar(7);not null;"`
// 	Price     float32 `gorm:"Type:real;not null;"`
// 	Time      int64   `gorm:"Type:bigint;not null;"`
// 	Tradetime int64   `gorm:"Type:bigint;not null;"`
// 	Volume    float32 `gorm:"not null"`
// }

type CurrentCryptoPrice struct {
	gorm.Model
	CoinAbv   string  `gorm:"Type:varchar(7);not null;unique;primary key;"`
	Price     float32 `gorm:"Type:real;not null;"`
	Timestamp uint64  `gorm:"Type:bigint;not null;"`
}

type PortfolioManager struct {
	gorm.Model
	CoinAbv       string  `gorm:"Type:varchar(7);not null;"`
	CoinAmount    float32 `gorm:"Type:real;not null;"`
	Delta         float32 `gorm:"Type:real;not null;"`
	WhenEntered   int64   `gorm:"Type:money;not null;"`
	StrategyUsing string  `gorm:"Type:varchar(20);not null;unique;primary key"`
	StopLoss      float32 `gorm:"Type:money;not null;"`
}

type CoinData struct {
	Name     string
	Abbr     string
	Priority uint8 `gorm:"Type:smallint"`
}
