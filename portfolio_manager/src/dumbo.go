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
	"strings"
	"time"

	"github.com/jinzhu/gorm"
	_ "github.com/jinzhu/gorm/dialects/postgres"
	log "github.com/sirupsen/logrus"
)

type dumbo struct {
	DBInterface *gorm.DB
}

func (Dumbo *dumbo) InitializeDB() {
	fmt.Println("Connecting to database")

	var err error
	global_db, err := Dumbo.ConnectDB(db_string, dbType)
	Dumbo.DBInterface = global_db
	if err != nil {
		//if we can't connect to db then panic and stop
		panic(err)
	}
	fmt.Println("Connected to database successfully")
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

/*
	ARGS:
        -> coins (*[]string): pointer to coin strings we use
    RETURN:
        -> (*map[string][]Candlestick): pointer to map between coin name and slice of candles
    WHAT:
		-> Retrieves all historic data up to the number of entries
*/
func (Dumbo *dumbo) GetAllPreviousCandles(coins *[]string, entries int) *map[string][]Candlestick {
	all_candles := map[string][]Candlestick{}
	for _, coin := range *coins {
		temp_coin_candles := []Candlestick{}
		err := Dumbo.DBInterface.Table(strings.ToLower(coin) + "_minute_kline").
			Limit(entries).Order("start_time asc").Find(&temp_coin_candles).Error
		if err != nil {
			log.Warn("Could not retrieve coin candle data", err)
		}
		coin_candles := temp_coin_candles
		//smooth
		i, gap_index := 0, 0
		for i < len(temp_coin_candles)-1 {
			if temp_coin_candles[i].StartTime+60 < temp_coin_candles[i+1].StartTime {
				num_gaps := int((temp_coin_candles[i+1].StartTime - temp_coin_candles[i].StartTime) / 60)

				gap_slice := make([]Candlestick, num_gaps-1)
				for j := 1; j < num_gaps; j++ {
					ratio := float64(j) / float64(num_gaps)
					gap_slice[i-1] = Candlestick{
						Open:      ratio*(temp_coin_candles[i+1].Open-temp_coin_candles[i].Open) + temp_coin_candles[i].Open,
						High:      ratio*(temp_coin_candles[i+1].High-temp_coin_candles[i].High) + temp_coin_candles[i].High,
						Low:       ratio*(temp_coin_candles[i+1].Low-temp_coin_candles[i].Low) + temp_coin_candles[i].Low,
						Close:     ratio*(temp_coin_candles[i+1].Close-temp_coin_candles[i].Close) + temp_coin_candles[i].Close,
						StartTime: temp_coin_candles[i].StartTime + int64((j * 60)),
						Volume:    (temp_coin_candles[i+1].Volume + temp_coin_candles[i].Volume) / 2,
						NumTrades: (temp_coin_candles[i+1].NumTrades + temp_coin_candles[i].NumTrades) / 2,
						coinName:  temp_coin_candles[i].coinName,
					}
				}
				second_half := coin_candles[gap_index+1:]
				coin_candles = append(coin_candles[:gap_index+1], gap_slice...)
				coin_candles = append(coin_candles, second_half...)
				gap_index += num_gaps
			} else {
				gap_index++
			}
			i++
		}
		all_candles[coin] = coin_candles
	}
	return &all_candles
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
