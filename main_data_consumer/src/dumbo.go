package main

import (
	"errors"
	"fmt"
	"log"
	"strconv"
	"strings"
	"time"

	"github.com/adshao/go-binance"

	"github.com/jinzhu/gorm"
	_ "github.com/jinzhu/gorm/dialects/postgres"
)

type dumbo struct{}

func (*dumbo) ConnectDB(database string, dbType string) (*gorm.DB, error) {
	const timeout = 1 * time.Minute
	tries := 0

	deadline := time.Now().Add(timeout)
	for tries = 0; time.Now().Before(deadline); tries++ {
		fmt.Println("dbType")
		db, err := gorm.Open(dbType, database)
		if err == nil {
			return db, nil
		}
		log.Printf("Could not connect to the database (%s). Retrying...", err.Error())
		time.Sleep(time.Second << uint(tries))
	}
	//Sleep for two seconds
	time.Sleep(2 * time.Second)
	return nil, fmt.Errorf("Failed to connect to the database of %d attempts", tries)
}

func (*dumbo) AutoMigrate(database *gorm.DB) error {
	return database.AutoMigrate(&HistoricalCrypto{}, &CurrentCryptoPrice{},
		&PortfolioManager{}).Error
}

func (*dumbo) StoreCrypto(event binance.WsTradeEvent) error {
	coin_abb := strings.Split(event.Symbol, "USDT")[0]
	price, err1 := strconv.ParseFloat(event.Price, 32)

	volume, err2 := strconv.ParseFloat(event.Quantity, 32)

	if err1 != nil || err2 != nil {
		fmt.Println("could not turn string into float")
		return errors.New(err1.Error() + err2.Error())
	}
	return global_db.Create(&HistoricalCrypto{CoinAbv: coin_abb,
		Price:     float32(price),
		Tradetime: event.TradeTime,
		Time:      event.Time,
		Volume:    float32(volume)}).Error

}

func (*dumbo) AddConstraint(database *gorm.DB) error {
	err := database.Exec("ALTER TABLE sentiments DROP CONSTRAINT IF EXISTS source_id;").Error
	if err != nil {
		return err
	}
	err = database.Exec("ALTER TABLE sentiments ADD CONSTRAINT source_id " +
		" UNIQUE (data_stream, unique_id);").Error
	if err != nil {
		return err
	}

	err = database.Exec("ALTER TABLE stocks DROP CONSTRAINT IF EXISTS unique_stock_point;").Error
	if err != nil {
		return err
	}
	return database.Exec("ALTER TABLE stocks ADD CONSTRAINT " +
		"unique_stock_point UNIQUE (symbol, timestamp);").Error
}
