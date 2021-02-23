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

func Float32Max(x, y float32) float32 {
	if x > y {
		return x
	}
	return y
}

func Float32Min(x, y float32) float32 {
	if x < y {
		return x
	}
	return y
}

func packageToSend(candlesticks *map[string]*Candlestick) *map[string]Candlestick {
	time_now := time.Now().Unix()
	packagedCandles := make(map[string]Candlestick)
	for coin, candle := range *candlesticks {
		candle.StartTime = time_now
		packagedCandles[coin] = *candle
	}
	return &packagedCandles
}
