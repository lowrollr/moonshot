// /*
// FILE: utils.go
// AUTHORS:
//     -> Ross Copeland <rhcopeland101@gmail.com>
// WHAT:
// 	-> Random functions that would muddy other files
// */
package main

import (
	"time"
)

/*
	ARGS:
		-> x (float32): number
		-> y (float32): number
    RETURN:
        -> (float32): number
    WHAT:
		-> returns larger number
*/
func Float32Max(x, y float32) float32 {
	if x > y {
		return x
	}
	return y
}

/*
	ARGS:
		-> price (*CoinPrice):
		-> src (int): id of the src of data consumer container (0)
		-> dest (int): destinition id for container
    RETURN:
        -> (float32): number
    WHAT:
		-> returns smaller number
*/
func Float32Min(x, y float32) float32 {
	if x < y {
		return x
	}
	return y
}

/*
	ARGS:
		-> candlesticks (*map[string]*Candlestick): pointer to map of coin name and pointer to candlestick data
    RETURN:
        -> (*map[string]Candlestick): Something that can be sent to other containers
    WHAT:
		-> Creates candlestick message that can be sent to other containers
*/
func packageToSend(candlesticks *map[string]*Candlestick) *map[string]Candlestick {
	time_now := time.Now().Unix()
	packagedCandles := make(map[string]Candlestick)
	for coin, candle := range *candlesticks {
		candle.StartTime = time_now
		packagedCandles[coin] = *candle
	}
	return &packagedCandles
}
