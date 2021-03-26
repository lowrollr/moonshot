/*
FILE: utils.go
AUTHORS:
	-> Jacob Marshall <marshingjay@gmail.com>
    -> Ross Copeland <rhcopeland101@gmail.com>
WHAT:
	-> Utility functions that don't have another home
*/
package main

import (
	"encoding/json"
	"os"
	"bufio"
	log "github.com/sirupsen/logrus"
)

/*
	ARGS:
		-> candleA (*Candlestick): older candle to smooth values after
		-> candleB (*Candlestick): newer candle to smooth values before
    RETURN:
        -> smoothedCandles (*[]Candlestick): list of candles to fill missing spaces between candleA and candleB 
    WHAT:
		-> Fills gap between two candles with generated candles, such that the values for each candle field are smoothed linearly between candleA and candleB
*/
func SmoothBetweenCandles(candleA *Candlestick, candleB *Candlestick) *[]Candlestick {
	// calculate how many candles need to be generated (amount of missing minutes between candle A and candle B)
	candlesNeeded := float64((candleB.Timestamp / 60) - (candleA.Timestamp / 60) - 1)
	smoothedCandles := []Candlestick{}
	if candlesNeeded > 0 {
		// we'll use this to store the generated candles
		smoothedCandles := make([]Candlestick, int(candlesNeeded))
		// calculated the difference between each field for candleA & candleB
		dClose := candleB.Close - candleA.Close
		dOpen := candleB.Open - candleA.Open
		dHigh := candleB.High - candleA.High
		dLow := candleB.Low - candleA.Low
		dVolume := candleB.Volume - candleA.Volume
		dTrades := float64(candleB.Trades - candleA.Trades)

		// fill in the missing fields
		// each field value can be calculated by (i * diff) / numGaps
		for i := float64(1); i <= candlesNeeded; i++ {
			smoothedCandles[int(i)-1] = Candlestick {
				Close: (i * dClose) / (candlesNeeded + 1),
				Open: (i * dOpen) / (candlesNeeded + 1),
				High: (i * dHigh) / (candlesNeeded + 1),
				Low: (i * dLow) / (candlesNeeded + 1),
				Volume: (i * dVolume) / (candlesNeeded + 1),
				Trades: int((i * dTrades) / (candlesNeeded + 1)),
				Timestamp: int64(float64(candleA.Timestamp) + (i * 60)),
			}
		}
	}
	// return the smoothed candles
	return &smoothedCandles
}

/*
	ARGS:
		-> N/A
    RETURN:
        -> coins (*[]string): a list of coin tickers
    WHAT:
		-> Retrieves coin tickers from 'coins.csv' and returns them in a slice
*/
func RetrieveCoins() *[]string {

	// open the csv file containing the coins we'll be trading
	f, err := os.Open("./coins.csv")
	if err != nil {
		log.Panic("Could not access coins csv file: ", err)
	}

	// close the file when we're done here
	defer f.Close()

	// store the coins in this slice
	var coins []string

	// read in coins from the csv
	scanner := bufio.NewScanner(f)
	for scanner.Scan() {
		coins = append(coins, scanner.Text())
	}

	// return the list of coins
	return &coins
}

func InterfaceToRawJSON(inter *map[string]interface{}) *map[string]json.RawMessage {
	rawJSONMap := make(map[string]json.RawMessage)
	for key, val := range *inter {
		valJSON, err := json.Marshal(&val)
		if err != nil {
			log.Panic("Could not marshal json: ", val)
		} else {
			rawJSONMap[key] = valJSON
		}
	}
	

	return &rawJSONMap
}