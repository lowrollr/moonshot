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
	// "sync"

	"github.com/jinzhu/gorm"
)

type OrderBook struct {
	BidPrice    float32 `gorm:"Type:real;not null;"`
	BidVolume   float32 `gorm:"Type:real;not null;"`
	AskPrice    float32 `gorm:"Type:real;not null;"`
	AskVolume   float32 `gorm:"Type:real;not null;"`
	Time        int64   `gorm:"type:bigint;not null"`
	PriorityVal int8    `gorm:"not null;"`
	coinName    string  `gorm:"-"`
}

type Candlestick struct {
	// *sync.Mutex `gorm:"-" json:"-"`
	Open        float64 `gorm:"Type:real;not null;" json:"open"`
	High        float64 `gorm:"Type:real;not null;" json:"high"`
	Low         float64 `gorm:"Type:real;not null;" json:"low"`
	Close       float64 `gorm:"Type:real;not null;" json:"close"`
	Volume      float64 `gorm:"Type:real;not null;" json:"volume"`
	NumTrades   int     `gorm:"not null;" json:"trades"`
	coinName    string  `gorm:"-"`
	StartTime   int64   `gorm:"type:bigint;not null" json:"time"`
}

type OHCLData struct {
	StartTime int64   `gorm:"Type:bigint;not null;"`
	EndTime   int64   `gorm:"Type:bigint;not null;"`
	Open      float32 `gorm:"Type:real;not null;"`
	High      float32 `gorm:"Type:real;not null;"`
	Low       float32 `gorm:"Type:real;not null;"`
	Close     float32 `gorm:"Type:real;not null;"`
	Volume    float32 `gorm:"Type:real;not null;"`
	coinName  string  `gorm:"-"`
}

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
