/*
FILE: dumbo.go
AUTHORS:
    -> Ross Copeland <rhcopeland101@gmail.com>
WHAT:
	-> Functions for interfacing with the database
*/
package main

import (
	"bufio"
	"fmt"
	"os"
	"strconv"
	"strings"
	"sync"
	"time"

	"github.com/jinzhu/gorm"
	_ "github.com/jinzhu/gorm/dialects/postgres"
	decimal "github.com/shopspring/decimal"
	log "github.com/sirupsen/logrus"
)

type dumbo struct {
	sync.Mutex
	DBInterface *gorm.DB
}

func (Local_Dumbo *dumbo) InitializeDB() {
	log.Println("Connecting to database")
	var err error
	global_db, err := Local_Dumbo.ConnectDB(db_string, dbType)

	if err != nil {
		//if we can't connect to db then panic and stop
		panic(err)
	}
	Local_Dumbo.DBInterface = global_db
	log.Println("Connected to database successfully")
}

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

func (Local_Dumbo *dumbo) StoreTrade(trade_type int, coin string, numCoins, executedValue, price, allocatedValue decimal.Decimal, fees string, profitVal float64) {
	Local_Dumbo.Lock()
	defer Local_Dumbo.Unlock()

	first_enter_const := decimal.NewFromInt(-100)
	first_exit_const := decimal.NewFromInt(100)
	sec_const := decimal.NewFromInt(-1)
	//calc slippage
	var slippage decimal.Decimal
	
	if trade_type == 0 {
		slippage = executedValue.Div(allocatedValue).Add(sec_const).Mul(first_enter_const)
	} else if trade_type == 1 {
		slippage = executedValue.Div(allocatedValue).Add(sec_const).Mul(first_exit_const)
		
	} else if trade_type == 2 {
		slippage = executedValue.Div(allocatedValue).Add(sec_const).Mul(first_exit_const)
	} else {
		log.Warn("Trades are either enter or exit. Not: ", trade_type)
	}
	//convert to float64
	sizeTrade, _ := numCoins.Float64()
	execCash, _ := executedValue.Float64()
	actualCash, _ := allocatedValue.Float64()
	cPrice, _ := price.Float64()
	feeVal, _ := strconv.ParseFloat(fees, 64)
	slipVal, _ := slippage.Float64()
	curTime := time.Now().Unix()

	temp_trade_entry := Trades{
		TradeType:     trade_type,
		coinName:      coin,
		SizeTrade:     sizeTrade,
		ExecutedValue: execCash,
		RealizedValue: actualCash,
		CoinPrice:     cPrice,
		Fees:          feeVal,
		Slippage:      slipVal,
		StartTime:     curTime,
		Profit: 	   profitVal,
	}
	err := Local_Dumbo.DBInterface.Table(strings.ToLower(coin) + "_trades").Create(&temp_trade_entry).Error
	if err != nil {
		log.Warn("Was not able to store trade. Err:", err)
	}

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
	f, err := os.Open("./coins.csv")
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
	} else {
		counter := 0
		for scanner.Scan() {
			if counter < n {
				coin_abr = append(coin_abr, scanner.Text())
				counter += 1
			} else {
				break
			}

		}
	}
	return &coin_abr
}
