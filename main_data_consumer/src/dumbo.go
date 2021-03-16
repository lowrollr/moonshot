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

	"github.com/ross-hugo/go-binance/v2"

	"github.com/jinzhu/gorm"
	_ "github.com/jinzhu/gorm/dialects/postgres"
	log "github.com/sirupsen/logrus"
)

type dumbo struct {
	DBInterface *gorm.DB
}

func (LocalDumbo *dumbo) InitializeDB() {
	fmt.Println("Connecting to database")

	var err error
	global_db, err := Dumbo.ConnectDB(db_string, dbType)
	LocalDumbo.DBInterface = global_db
	if err != nil {
		//if we can't connect to db then panic and stop
		panic(err)
	}
	fmt.Println("Connected to database successfully")

	fmt.Println("Creating tables in database")
	err = LocalDumbo.AutoMigrate()
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
func (LocalDumbo *dumbo) AutoMigrate() error {
	//Create tables specified in models.go
	//get coins
	coins := LocalDumbo.SelectCoins(-1)
	for _, coin := range *coins {
		temp_order := OrderBook{coinName: strings.ToLower(coin) + "_order_book"}
		temp_min_kline := Candlestick{coinName: strings.ToLower(coin) + "_minute_kline"}
		temp_custom_kline := OHCLData{coinName: strings.ToLower(coin) + "_custom_kline"}
		temp_trades := Trades{coinName: strings.ToLower(coin) + "_trades"}
		err := LocalDumbo.DBInterface.AutoMigrate(&temp_order,
			&temp_min_kline, &temp_custom_kline, &temp_trades).Error
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
func (m Candlestick) TableName() string {
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
func (f Trades) TableName() string {
	if f.coinName != "" {
		return strings.ToLower(f.coinName)
	}
	return "trades"
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
func (LocalDumbo *dumbo) StoreCryptoBidAsk(event *binance.WsPartialDepthEvent) error {
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
		err = LocalDumbo.DBInterface.Table(strings.ToLower(coin_abb) + "_order_book").Create(&temp_order_entry).Error
		if err != nil {
			return err
		}
	}

	return nil
}

/*
	ARGS:
		-> event (*map[string]*Candlestick): pointer to object that has all kline information for all coins
		-> wg (*sync.WaitGroup): used to sync different goroutines
    RETURN:
        -> N/A
    WHAT:
		-> Inserts ohcl data into db
*/
func (LocalDumbo *dumbo) StoreAllCandles(event *map[string]*Candlestick, wg *sync.WaitGroup) {
	defer wg.Done()
	for coin, candleData := range *event {
		candleData.StartTime = candleData.StartTime * 60
		err := LocalDumbo.DBInterface.Table(strings.ToLower(coin) + "_minute_kline").
			Create(candleData).Error

		if err != nil {
			log.Warn("Was not able to store candle for coin: " + coin)
		}
	}
}

/*
	ARGS:
        -> event (map[string]*OHCLData): pointer to object that has all kline information
    RETURN:
        -> (error): returns if there is one, an error in inserting coin data in the database
    WHAT:
		-> Inserts volume and trade coin data into database
*/
func (LocalDumbo *dumbo) StoreCryptosCandle(all_coin_candles map[string]*OHCLData) error {
	for symbol, data := range all_coin_candles {
		err := LocalDumbo.DBInterface.Table(strings.ToLower(symbol) + "_custom_kline").Create(data).Error
		if err != nil {
			return err
		}
	}
	return nil
}

/*
	ARGS:
        -> coins (*[]string): pointer to coin strings we use
    RETURN:
        -> (*map[string][]Candlestick): pointer to map between coin name and slice of candles
    WHAT:
		-> Retrieves all historic data up to the number of entries
*/
func (LocalDumbo *dumbo) GetAllPreviousCandles(coins *[]string, entries int) (*map[string][]Candlestick, bool) {
	all_candles := map[string][]Candlestick{}
	send_more_smoothed := false

	for _, coin := range *coins {
		temp_coin_candles := []Candlestick{}
		err := LocalDumbo.DBInterface.Table(strings.ToLower(coin) + "_minute_kline").
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

		curTime := time.Now()
		if len(coin_candles) > 0 {
			if coin_candles[len(coin_candles)-1].StartTime < curTime.Add(-time.Minute).Unix() {
				send_more_smoothed = true
			}
		}

		all_candles[coin] = coin_candles
	}
	return &all_candles, send_more_smoothed
}

func (LocalDumbo *dumbo) GetAllPMData(coins *[]string, coin_entries, trade_entries int) (*TradesAndCandles, bool) {
	all_candles, send_more_smoothed := LocalDumbo.GetAllPreviousCandles(coins, coin_entries)
	prev_trades := LocalDumbo.GetTradesAfterExit(coins)
	all_trades := make(map[string][]float64, len(*coins))
	for _, coin := range *coins {
		temp_trades := []Trades{}
		err := LocalDumbo.DBInterface.Table(strings.ToLower(coin)+"_trades").
			Limit(coin_entries).Where("trade_type = ?", "2").Order("start_time asc").Find(&temp_trades).Error
		if err != nil {
			log.Warn("Could not retrieve trades from coin:", coin, "With error:", err)
		}
		for _, trade := range temp_trades {
			all_trades[coin] = append(all_trades[coin], trade.Profit)
		}
	}
	all_candles_and_trades := TradesAndCandles{
		Profits: all_trades,
		Coins:   *all_candles,
		TradeHistory: *prev_trades,
	}
	return &all_candles_and_trades, send_more_smoothed
}

func (LocalDumbo *dumbo) GetLastCandles(coins *[]string) *map[string]Candlestick {
	last_candles := map[string]Candlestick{}
	for _, coin := range *coins {
		temp_candle := Candlestick{}
		err := LocalDumbo.DBInterface.Table(strings.ToLower(coin) + "_minute_kline").
			First(&temp_candle).Order("start_time desc").Error
		if err != nil {
			log.Warn("Error retrieving the first entry of candle. From coin:", coin, "With error:", err)
		}
		last_candles[coin] = temp_candle
	}
	return &last_candles
}

func (LocalDumbo *dumbo) GetTradesAfterExit(coins *[]string) *map[string][]Trades {
	p_exit_trades := map[string][]Trades{}
	for _, coin := range *coins {
		table_name := strings.ToLower(coin) + "_trades"
		raw_sql := "SELECT * FROM " + table_name + ` WHERE start_time > (SELECT coalesce((SELECT MAX(start_time) FROM ` + table_name + ` WHERE trade_type=2), 0)) ORDER BY start_time DESC;`
		temp_trades := []Trades{}
		err := LocalDumbo.DBInterface.Raw(raw_sql).Scan(&temp_trades).Error
		
		
		
		if err != nil {
			log.Warn(err)
		} 
		
		
		
		p_exit_trades[coin] = temp_trades
		
	}
	return &p_exit_trades
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
