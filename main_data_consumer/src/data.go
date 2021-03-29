/*
FILE: data.go
AUTHORS:
	-> Jacob Marshall <marshingjay@gmail.com>
    -> Ross Copeland <rhcopeland101@gmail.com>
WHAT:
	-> Functions for interfacing with the database
*/
package main

import (
	"strconv"
	"strings"
	"time"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
	log "github.com/sirupsen/logrus"
)



func (dc *DataConsumer) InitializeDB() {
	log.Println("Connecting to database...")

	// initialize the database connection
	dbConnection := ConnectDB(db_string, dbType)
	
	dc.Database = dbConnection
	
	log.Println("Connected to database successfully")

	log.Println("Creating tables in database")
	dc.AutoMigrate()
	
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
func ConnectDB(database string, dbType string) (*gorm.DB) {
	//Trying to connect to database for a minute, otherwise panic
	const timeout = 1 * time.Minute
	tries := 0

	deadline := time.Now().Add(timeout)
	//Iterating through the amount of tries to connect to database
	for tries = 0; time.Now().Before(deadline); tries++ {
		db, err := gorm.Open(postgres.Open(db_string), &gorm.Config{})
		if err == nil {
			return db
		}
		log.Printf("Could not connect to the database (%s). Retrying...", err.Error())
		time.Sleep(time.Second << uint(tries))
	}
	//Sleep for two seconds
	time.Sleep(2 * time.Second)
	log.Panic("Failed to connect to the database of %d attempts", tries)
	return nil
}

/*
	ARGS:
        -> N/A
    RETURN:
        -> 
    WHAT:
		->
*/
func (dc *DataConsumer) AutoMigrate() {
	
	for _, coin := range *dc.Coins {
		
		minCandle := Candlestick{}
		dc.Database.Table(strings.ToLower(coin) + "_1m_candles").AutoMigrate(&minCandle)
		trades := Trade{coinName: strings.ToLower(coin) + "_trades"}
		dc.Database.Table(strings.ToLower(coin) + "_trades").AutoMigrate(&trades)
		
	}
	pbal := PortfolioBalance{}
	dc.Database.AutoMigrate(&pbal)
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
func (dc *DataConsumer) StoreCandles(event *map[string]*Candlestick) {
	for coin, candleData := range *event {
		err := dc.Database.Table(strings.ToLower(coin) + "_1m_candles").
			Create(candleData).Error

		if err != nil {
			log.Warn("Was not able to store candle for coin: " + coin)
		}
	}
}


/*
	RECEIVER:
		-> dc (*DataConsumer): core Data Consumer object
	ARGS:
        -> N/A
    RETURN:
        -> 
    WHAT:
		-> 
*/
func (dc *DataConsumer) GetBalanceHistory(prevMinutes int64) *[]PortfolioBalance {
	balances := []PortfolioBalance{}
	howFarToGoBack := time.Now().Add(-1 * time.Minute * time.Duration(prevMinutes)).Unix()
	dc.Database.Table("portfolio_balances").Where("timestamp >= ?", howFarToGoBack).Order("timestamp asc").Find(&balances)
	return &balances
}

func (dc *DataConsumer) GetDWMYClosePrices() *map[string]map[string][]ClosePrice {
	allResults := make(map[string]map[string][]ClosePrice)
	for _, coin := range *dc.Coins {
		// get last day's worth of data 
		howFarToGoBack := time.Now().Add(-1 * time.Minute * time.Duration(1440)).Unix()
		dayData := []ClosePrice{}
		dc.Database.Table(strings.ToLower(coin) + "_1m_candles").Where("timestamp >= ?", howFarToGoBack).Order("timestamp asc").Find(&dayData)
		weekData := []ClosePrice{}
		dc.Database.Table(strings.ToLower(coin) + "_1m_candles").Where("timestamp >= ? AND timestamp % 420 = 0", howFarToGoBack * 7).Order("timestamp asc").Find(&weekData)
		monthData := []ClosePrice{}
		dc.Database.Table(strings.ToLower(coin) + "_1m_candles").Where("timestamp >= ? AND timestamp % 1800 = 0", howFarToGoBack * 30).Order("timestamp asc").Find(&monthData)
		yearData := []ClosePrice{}
		dc.Database.Table(strings.ToLower(coin) + "_1m_candles").Where("timestamp >= ? AND timestamp % 21900 = 0", howFarToGoBack * 365).Order("timestamp asc").Find(&yearData)
		timespanMap := make(map[string][]ClosePrice)
		timespanMap["d"] = dayData
		timespanMap["w"] = weekData
		timespanMap["m"] = monthData
		timespanMap["y"] = yearData
		allResults[coin] = timespanMap
	}
	return &allResults
}

func (dc *DataConsumer) GetDWMYPortfolioBalances() *map[string][]PortfolioBalance {

	// get last day's worth of data 
	howFarToGoBack := time.Now().Add(-1 * time.Minute * time.Duration(1440)).Unix()
	dayData := []PortfolioBalance{}
	dc.Database.Table("portfolio_balances").Where("timestamp >= ?", howFarToGoBack).Order("timestamp asc").Find(&dayData)
	weekData := []PortfolioBalance{}
	dc.Database.Table("portfolio_balances").Where("timestamp >= ? AND timestamp % 420 = 0", howFarToGoBack * 7).Order("timestamp asc").Find(&weekData)
	monthData := []PortfolioBalance{}
	dc.Database.Table("portfolio_balances").Where("timestamp >= ? AND timestamp % 1800 = 0", howFarToGoBack * 30).Order("timestamp asc").Find(&monthData)
	yearData := []PortfolioBalance{}
	dc.Database.Table("portfolio_balances").Where("timestamp >= ? AND timestamp % 21900 = 0", howFarToGoBack * 365).Order("timestamp asc").Find(&yearData)
	timespanMap := make(map[string][]PortfolioBalance)
	timespanMap["d"] = dayData
	timespanMap["w"] = weekData
	timespanMap["m"] = monthData
	timespanMap["y"] = yearData
	return &timespanMap
	
}



func (dc *DataConsumer) GetTradeHistory(numTrades int64) *map[string][]Trade {
	trades := make(map[string][]Trade)
	for _, coin := range *dc.Coins {
		exits := []Trade{}
		enters := []Trade{}
		all := []Trade{}

		dc.Database.Table(strings.ToLower(coin) + "_trades").Where("type_id = ?", "2").Limit(int(numTrades)).Order("timestamp asc").Find(&exits)
		if len(exits) > 0 {
			// get timestamp of last exit
			lastExitTimestamp := exits[len(exits) - 1].Timestamp

			dc.Database.Table(strings.ToLower(coin) + "_trades").Where("type_id = ? AND timestamp < ?", "0", strconv.FormatInt(lastExitTimestamp, 10)).Limit(int(numTrades)).Order("timestamp asc").Find(&enters)
			if len(enters) > 0 {
				firstEnterTimestamp := enters[0].Timestamp

				dc.Database.Table(strings.ToLower(coin) + "_trades").Where("timestamp <= ? AND timestamp >= ?", strconv.FormatInt(lastExitTimestamp, 10), strconv.FormatInt(firstEnterTimestamp, 10)).Order("timestamp asc").Find(&all)
			}
			
		}
		trades[coin] = all
	}

	return &trades
}


/*
	RECEIVER:
		-> dc (*DataConsumer): core Data Consumer object
	ARGS:
        -> N/A
    RETURN:
        -> 
    WHAT:
		-> 
*/
func (dc *DataConsumer) GetOpenTrades() *map[string][]Trade {
	openTrades := make(map[string][]Trade)

	for _, coin := range *dc.Coins {
		tableName := strings.ToLower(coin) + "_trades"
		// I don't know how to write this query with gorm functions so here's the raw query
		rawSql := "SELECT * FROM " + tableName + ` WHERE timestamp > (SELECT coalesce((SELECT MAX(timestamp) FROM ` + tableName + ` WHERE type_id=2), 0)) ORDER BY timestamp ASC;`
		
		trades := []Trade{}

		dc.Database.Raw(rawSql).Scan(&trades)
		openTrades[coin] = trades
	}
	return &openTrades
}

/*
	RECEIVER:
		-> dc (*DataConsumer): core Data Consumer object
	ARGS:
        -> numTrades (int64): how many past trade profit percentages should be received
    RETURN:
        -> tradeProfits (map[string][]float64): maps coin -> profit percentage array
    WHAT:
		-> For each coin, retrieves an array of profit percentages corresponding to the last X trades performed on the given coin
*/
func (dc *DataConsumer) GetTradeProfits(numTrades int64) *map[string][]float64 {
	// we'll return a map from coins to lists of profit percentages -- we'll store that here
	tradeProfits := make(map[string][]float64)
	
	// build an array of past profit percentages for each coin
	for _, coin := range *dc.Coins {
		// we'll need an array to read in the trades from the database to
		trades := []Trade{}

		// query the database for the <numTrades> most recent trades
		dc.Database.Table(strings.ToLower(coin) + "_trades").Where("type_id = ?", "2").Limit(int(numTrades)).Order("timestamp desc").Find(&trades)

		// create an array to store the profit percentages in
		profits := make([]float64, numTrades)
		// grab each profit percentage from the trades we received
		for index, trade := range trades{
			// note that the trades we receive will be in reverse order (see query), we want to store them chronologically
			profits[numTrades - 1 - int64(index)] = trade.Profit
		}

		// store our profit array in the map for this coin
		tradeProfits[coin] = profits
	}
	
	// return the coin -> profit percentage array map
	return &tradeProfits
}

/*
	RECEIVER:
		-> dc (*DataConsumer): core Data Consumer object
	ARGS:
        -> prevCandles (int64): how many past candles should be retrieved
    RETURN:
        -> N/A
    WHAT:
		-> Returns candles encompassing the previous <given amount> of minutes
			-> smooths gaps as necessary for candles that are not in the database
	TODO:
		-> adapt this function to be able to fetch differnt candle sizes (assumes 1m candles)
*/
func (dc *DataConsumer) GetCandleData(prevCandles int64) *map[string][]Candlestick {

	// initialize the map from coin -> candle array
	candles := make(map[string][]Candlestick)

	// get the earliest time we'll consider candles for (now - X minutes)
	// note: using time.Add() here is necessary, time.Sub() does not do what you want it to do
	// we subtract 1 from prevCandles, because the most recent candle we return will be fetched live from coinbase
	startTimeWindow := time.Now().Add(-1 * time.Minute * time.Duration(prevCandles)).Unix()

	// fill in arrays with historical candle data, smooth as needed if there are gaps
	for _, coin := range *dc.Coins {
		// keeps track of how many candles we've added to our solution so far (to track index)
		candlesAdded := 0

		// initialize each array to be of len(prevCandles), that's exactly how many we need to store
		candles[coin] = make([]Candlestick, prevCandles)

		// construct a temporary Candle array struct to put the retrieved candles into
		// there could be gaps between these candles, which is why they aren't read directly into the array in the map
		var retrievedCandles []Candlestick
		
		// get candles that match our time constraint
		dc.Database.Table(strings.ToLower(coin) + "_1m_candles").Where("timestamp >= ?", startTimeWindow).Order("timestamp asc").Find(&retrievedCandles)
		
		// check if any candles were retrieved
		if len(retrievedCandles) > 0 {
			// check if the first candle receieved occurs at exactly the beginning of the window
			// we'll round this to the nearest minute
			// if it does we can transition to the main section of the algorithm
			if startTimeWindow / 60 != retrievedCandles[0].Timestamp / 60 {
				// if it doesn't (special case) we need to find the next most previous candle and smooth the data between that candle and our first candle
				// get the next most previous candle 
				var prevCandle Candlestick
				dc.Database.Table(strings.ToLower(coin) + "_1m_candles").Where("timestamp < ?", startTimeWindow).Order("timestamp desc").First(&prevCandle)
				if prevCandle.Timestamp != 0 {
					// smooth the values in between 
					smoothedCandles := SmoothBetweenCandles(&prevCandle, &retrievedCandles[0])

					// filter out the values we actually need (only those that fall within our time boundary)
					for _, candle := range *smoothedCandles {
						if candle.Timestamp >= startTimeWindow {
							candles[coin][candlesAdded] = candle
							candlesAdded++
						}
					}
				}
				
			}

			// we'll need to keep track of the last candle accessed (for comparing subsequent candles)
			// let's go ahead and store the first candle we received from our db query
			lastCandle := retrievedCandles[0]

			// we actually just examined this candle, and we know that it is either is the first candle within our timespan
			// or the missing values before it have already been filled in, so it is safe to add to our final candle array
			candles[coin][candlesAdded] = retrievedCandles[0]
			candlesAdded++
			
			// iterate through each candle retrieved 
			// smooth between each gap as necessary
			for _, candle := range retrievedCandles[1:len(retrievedCandles)] {
				// check if each candle is directly after the previous candle
				if (candle.Timestamp / 60) + 1 == (lastCandle.Timestamp / 60) {
					// if it is, add it to the solution
					candles[coin][candlesAdded] = candle
					candlesAdded++
				} else {
					// if it's not, we need to smooth the values in between
					smoothedCandles := SmoothBetweenCandles(&lastCandle, &candle)
					// then add each smoothed candle to our solution, and finally 'candle' itself
					for _, smoothedCandle := range *smoothedCandles {
						candles[coin][candlesAdded] = smoothedCandle
						candlesAdded++
					}
					candles[coin][candlesAdded] = candle
					candlesAdded++
				}
			}
			// store the last candle in memory
			dc.LastCandleRetrieved[coin] = &retrievedCandles[len(retrievedCandles) - 1]
		} else {
			// smoothing the entire period (or more) is pretty silly, we just won't return any data for this coin and let the user know
			log.Warn("No candles retrieved for coin ", coin, " within the last ", prevCandles, " periods, data may be missing!")
		}
		candles[coin] = candles[coin][0:candlesAdded]
	}

	return &candles
}

