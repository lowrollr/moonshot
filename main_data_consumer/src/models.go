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
	Open      float64 `gorm:"Type:real;not null;" json:"open"`
	High      float64 `gorm:"Type:real;not null;" json:"high"`
	Low       float64 `gorm:"Type:real;not null;" json:"low"`
	Close     float64 `gorm:"Type:real;not null;" json:"close"`
	Volume    float64 `gorm:"Type:real;not null;" json:"volume"`
	NumTrades int     `gorm:"not null;" json:"trades"`
	coinName  string  `gorm:"-"`
	StartTime int64   `gorm:"type:bigint;not null" json:"time"`
}

type Trade struct {
	TypeId     int   `gorm:"not null;"`  // id corresponding to type of trade, 0 = enter, 1 = partial exit, 2 = exit
	coinName      string  `gorm:"-"` // coin traded
	Units     float64 `gorm:"Type:real;not null;"` // units of coin traded
	ExecutedValue float64 `gorm:"Type:real;not null;"` // cash we spent or receieved purshasing/selling the asset (excl. fees)
	Fees          float64 `gorm:"Type:real;not null;"` // cash we spent on paying transaction fees
	Profit        float64 `gorm:"Type:real;"` // percentage profit made on trade (only on full exits)
	Slippage      float64 `gorm:"Type:real; not null;"` // percent difference between desired price and actual average fill price
	Timestamp     int64   `gorm:"Type:bigint;not null"` // time this trade occured (in unix)
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
