/*
FILE: dumbo.go
AUTHORS:
    -> Ross Copeland <rhcopeland101@gmail.com>
WHAT:
	-> Functions for interfacing with the database
*/
package main

import (
	"fmt"
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

func (Local_Dumbo *dumbo) StorePortfolioValue(portfolioValue float64){
	Local_Dumbo.Lock()
	defer Local_Dumbo.Unlock()

	portfolioBalance := PortfolioBalance{
		Timestamp: time.Now().Unix(),
		Balance: portfolioValue,
	}

	err := Local_Dumbo.DBInterface.Table("balance_history").Create(&portfolioBalance).Error
	if err != nil {
		log.Warn("Was not able to store portfolio balance. Err:", err)
	}
}

func (Local_Dumbo *dumbo) StoreTrade(typeId int, coin string, units decimal.Decimal, execValue decimal.Decimal, fees decimal.Decimal, targetPrice float64, profit float64) {
	Local_Dumbo.Lock()
	defer Local_Dumbo.Unlock()

	unitsFl, _ := units.Float64()
	execValueFl, _ := execValue.Float64()
	avgFillPriceFl, _ := (execValue.Div(units)).Float64()
	feesFl, _ := fees.Float64()

	slipCoef := 100.0
	if typeId == 0 {
		slipCoef = -100.0
	}

	slippage := ((avgFillPriceFl / targetPrice) - 1.0) * slipCoef
	curTime := time.Now().Unix()

	temp_trade_entry := Trade{
		TypeId:			typeId,
		coinName:      	coin,
		Units:     		unitsFl,
		ExecutedValue: 	execValueFl,
		Fees:          	feesFl,
		Slippage:      	slippage,
		Timestamp:     	curTime,
		Profit: 	   	profit,
	}

	err := Local_Dumbo.DBInterface.Table(strings.ToLower(coin) + "_trades").Create(&temp_trade_entry).Error
	if err != nil {
		log.Warn("Was not able to store trade. Err:", err)
	}

}

