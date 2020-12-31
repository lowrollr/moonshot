/*
FILE: dumbo.go
AUTHORS:
    -> Ross Copeland <rhcopeland101@gmail.com>
WHAT:
	-> Functions for interfacing with the database
*/
package main

import (
	"errors"
	"fmt"
	"log"
	"strconv"
	"strings"
	"time"
	"io/ioutil"
	"os"
	"bufio"

	"github.com/adshao/go-binance"

	"github.com/jinzhu/gorm"
	_ "github.com/jinzhu/gorm/dialects/postgres"
)

type dumbo struct{}

/*
	ARGS:
		-> database (string): string for connecting to database. Specified through the env file
		-> dbType (string): type of database using. Specified through the env file
    RETURN:
        -> (*gorm.DB): returns pointer to object that talks to database
    WHAT:
		-> Initial connection to the database
		-> Verfies that it can connect to the database
*/
func (*dumbo) ConnectDB(database string, dbType string) (*gorm.DB, error) {
	//Trying to connect to database for a minute, otherwise panic
	const timeout = 1 * time.Minute
	tries := 0

	deadline := time.Now().Add(timeout)
	//Iterating through the amount of tries to connect to database
	for tries = 0; time.Now().Before(deadline); tries++ {
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

/*
	ARGS:
        -> N/A
    RETURN:
        -> error if there is one in table creation in database
    WHAT:
		-> Creates the tables in the database
*/
func (*dumbo) AutoMigrate() error {
	//Create tables specified in models.go
	return global_db.AutoMigrate(&HistoricalCrypto{}, &CurrentCryptoPrice{},
		&PortfolioManager{}, &CoinData{}).Error
}

/*
	ARGS:
        -> N/A
    RETURN:
        -> (error): Error if coin names were not deleted
    WHAT:
		-> Deletes all names and abbreviations of coins
		-> Used so coin_data does not continually grow
    TODO:
		-> Find better way to do this, Unique Abreviation/id
*/
func (*dumbo) deleteCoinIndex() error {
	return global_db.Where("1=1").Delete(&CoinData{}).Error
}

/*
	ARGS:
        -> event (binance.WsTradeEvent): object that has all binance trade information
    RETURN:
        -> (error): returns if there is one, an error in inserting coin data in the database
    WHAT:
		-> Inserts coin data into database
    TODO:
		-> Is there a better way to store Unix timestamp
*/
func (*dumbo) StoreCrypto(event binance.WsTradeEvent) error {
	//Getting information needed to store
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

/*
	ARGS:
        -> coin_data (*[]CoinData): list of coin names and abrevs to be stored
    RETURN:
        -> (error): returns error if one occurs
    WHAT:
		-> Stores the scraped coin data
*/
func (*dumbo) storeScraped(coin_data *[]CoinData) error {
	for _, coin := range *coin_data {
		err := global_db.Create(&coin).Error
		if err != nil {
			return err
		}
	}
	return nil
}

/*
	ARGS:
		-> n (int): Number of coins you want to select from indexed coins
			-> use -1 if you want all coins in db
    RETURN:
        -> (*[]string): returns pointer to slice of coin abrevs
    WHAT:
		-> Retrieves coin abrevs from database but only n
*/
func (*dumbo) SelectCoins(n int) *[]string {
	f, err := os.Open("coins.csv")
	if err != nil {
		panic(err)
	}

	defer f.Close()
	var coin_abr []string
	scanner := bufio.NewScanner(f)
	if n == -1 {
		for scanner.Scan() {
			coin_abr = append(coin_abr, scanner.Text())
		}
	}
	else {
		counter := 0
		for scanner.Scan() {
			if counter < n {
				coin_abr = append(coin_abr, scanner.Text())
				counter += 1
			}
			else {
				break
			}
			
		}
	}
	
	return &coin_abr
}
