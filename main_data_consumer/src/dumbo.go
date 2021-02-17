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
	"log"
	"os"
	"strconv"
	"strings"
	"time"

	"github.com/ross-hugo/go-binance/v2"

	"github.com/jinzhu/gorm"
	_ "github.com/jinzhu/gorm/dialects/postgres"
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

	fmt.Println("Creating tables in database")
	err = Dumbo.AutoMigrate()
	if err != nil {
		panic(err)
	}
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
        -> N/A
    RETURN:
        -> error if there is one in table creation in database
    WHAT:
		-> Creates the tables in the database
*/
func (Dumbo *dumbo) AutoMigrate() error {
	//Create tables specified in models.go
	//get coins
	coins := Dumbo.SelectCoins(-1)
	for _, coin := range *coins {
		temp_order := OrderBook{coinName: strings.ToLower(coin) + "_order_book"}
		temp_min_kline := MinuteKline{coinName: strings.ToLower(coin) + "_minute_kline"}
		temp_custom_kline := OHCLData{coinName: strings.ToLower(coin) + "_custom_kline"}
		err := Dumbo.DBInterface.AutoMigrate(&temp_order, &temp_min_kline, &temp_custom_kline).Error
		if err != nil {
			return err
		}
	}
	return nil
}

/*
	ARGS:
        -> N/A
    RETURN:
        -> (string): name of the coin for the database table
    WHAT:
		-> Returns the name of the coin so that it is a dynamic table names
*/
func (m MinuteKline) TableName() string {
	// double check here, make sure the table does exist!!
	if m.coinName != "" {
		return strings.ToLower(m.coinName)
	}
	return "coin_minute_kline" // default table name
}

/*
	ARGS:
        -> N/A
    RETURN:
        -> (string): name of the coin for the database table
    WHAT:
		-> Returns the name of the coin so that it is a dynamic table names
*/
func (o OrderBook) TableName() string {
	// double check here, make sure the table does exist!!
	if o.coinName != "" {
		return strings.ToLower(o.coinName)
	}
	return "order_book" // default table name
}

/*
	ARGS:
        -> N/A
    RETURN:
        -> (string): name of the coin for the database table
    WHAT:
		-> Returns the name of the coin so that it is a dynamic table names
*/
func (o OHCLData) TableName() string {
	// double check here, make sure the table does exist!!
	if o.coinName != "" {
		return strings.ToLower(o.coinName)
	}
	return "custom_kline" // default table name
}

/*
	ARGS:
        -> event (binance.WsTradeEvent): object that has all binance trade information
    RETURN:
        -> (error): returns if there is one, an error in inserting coin data in the database
    WHAT:
		-> Inserts coin data into database
*/
func (Dumbo *dumbo) StoreCryptoBidAsk(event *binance.WsPartialDepthEvent) error {
	//Getting information needed to store
	coin_abb := strings.Split(strings.ToLower(event.Symbol), "usdt")[0]

	update_time := time.Now().Unix()

	for i := 0; i < len(event.Bids); i++ {
		bidPrice, err := strconv.ParseFloat(event.Bids[i].Price, 32)
		bidVol, err := strconv.ParseFloat(event.Bids[i].Quantity, 32)
		askPrice, err := strconv.ParseFloat(event.Asks[i].Price, 32)
		askVol, err := strconv.ParseFloat(event.Asks[i].Quantity, 32)

		temp_order_entry := OrderBook{
			BidPrice:    float32(bidPrice),
			BidVolume:   float32(bidVol),
			AskPrice:    float32(askPrice),
			AskVolume:   float32(askVol),
			Time:        update_time,
			PriorityVal: int8(i),
		}
		err = Dumbo.DBInterface.Table(strings.ToLower(coin_abb) + "_order_book").Create(&temp_order_entry).Error
		if err != nil {
			return err
		}
	}

	return nil
}

/*
	ARGS:
        -> event (*binance.WsKlineEvent): pointer to object that has all kline information
    RETURN:
        -> (error): returns if there is one, an error in inserting coin data in the database
    WHAT:
		-> Inserts volume and trade coin data into database
*/
func (Dumbo *dumbo) StoreCryptoKline(event *binance.WsKlineEvent) error {
	coin_abb := strings.Split(strings.ToLower(event.Symbol), "usdt")[0]

	kline_time := event.Time

	kline := event.Kline

	open, _ := strconv.ParseFloat(kline.Open, 32)
	high, _ := strconv.ParseFloat(kline.High, 32)
	low, _ := strconv.ParseFloat(kline.Low, 32)
	close, _ := strconv.ParseFloat(kline.Close, 32)

	base_vol, _ := strconv.ParseFloat(kline.Volume, 32)

	// num_trades, err := strconv.ParseInt(event.Kline.TradeNum, 10, 16 )

	temp_kline := MinuteKline{StartTime: kline.StartTime, EndTime: kline.EndTime,
		Open: float32(open), High: float32(high), Low: float32(low), Close: float32(close),
		Volume: float32(base_vol), Trades: uint32(event.Kline.TradeNum), Time: kline_time}

	return Dumbo.DBInterface.Table(strings.ToLower(coin_abb) + "_minute_kline").Create(&temp_kline).Error
}

/*
	ARGS:
        -> event (map[string]*OHCLData): pointer to object that has all kline information
    RETURN:
        -> (error): returns if there is one, an error in inserting coin data in the database
    WHAT:
		-> Inserts volume and trade coin data into database
*/
func (Dumbo *dumbo) StoreCryptosCandle(all_coin_candles map[string]*OHCLData) error {
	for symbol, data := range all_coin_candles {
		err := Dumbo.DBInterface.Table(strings.ToLower(symbol) + "_custom_kline").Create(data).Error
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
