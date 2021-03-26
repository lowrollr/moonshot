/*
FILE: models.go
AUTHORS:
	-> Jacob Marshall <marshingjay@gmail.com>
    -> Ross Copeland <rhcopeland101@gmail.com>
WHAT:
	-> Structs defined here correspond to table in database
*/
package main

type Candlestick struct {
	// *sync.Mutex `gorm:"-" json:"-"`
	Open      float64 `gorm:"Type:real;not null;" json:"open"`
	High      float64 `gorm:"Type:real;not null;" json:"high"`
	Low       float64 `gorm:"Type:real;not null;" json:"low"`
	Close     float64 `gorm:"Type:real;not null;" json:"close"`
	Volume    float64 `gorm:"Type:real;not null;" json:"volume"`
	Trades 	  int     `gorm:"not null;" json:"trades"`
	coinName  string  `gorm:"-"`
	Timestamp int64   `gorm:"Type:bigint;not null;" json:"time"`
}

type Trade struct { // stores a single trade's information
	TypeId        int   `gorm:"not null;"`  // id corresponding to type of trade, 0 = enter, 1 = partial exit, 2 = exit
	coinName      string  `gorm:"-"` // coin traded
	Units     	  float64 `gorm:"Type:real;not null;"` // units of coin traded
	ExecutedValue float64 `gorm:"Type:real;not null;"` // cash we spent or receieved purshasing/selling the asset (excl. fees)
	Fees          float64 `gorm:"Type:real;not null;"` // cash we spent on paying transaction fees
	Profit        float64 `gorm:"Type:real;"` // percentage profit made on trade (only on full exits)
	Slippage      float64 `gorm:"Type:real; not null;"` // percent difference between desired price and actual average fill price
	Timestamp     int64   `gorm:"Type:bigint;not null"` // time this trade occured (in unix)
}

type PortfolioBalance struct { // stores the balance of the portfolio at a given timestamp
	Balance float64 `gorm:"Type:real;not null;"` // portfolio balance
	Timestamp     int64   `gorm:"Type:bigint;not null"` // timestamp of balance
}

