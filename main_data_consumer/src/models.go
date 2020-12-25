package main

import (
	"github.com/jinzhu/gorm"
)

type HistoricalCrypto struct {
	gorm.Model
	CoinAbv   string  `gorm:"Type:varchar(7);not null;"`
	Price     float32 `gorm:"Type:real;not null;"`
	Time      int64   `gorm:"Type:bigint;not null;"`
	Tradetime int64   `gorm:"Type:bigint;not null;"`
	Volume    float32 `gorm:"not null"`
}

type CurrentCryptoPrice struct {
	gorm.Model
	CoinAbv   string  `gorm:"Type:varchar(7);not null;unique;primary key;"`
	Price     float32 `gorm:"Type:real;not null;"`
	Timestamp int64   `gorm:"Type:bigint;not null;"`
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
