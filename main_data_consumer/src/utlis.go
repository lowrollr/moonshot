// /*
// FILE: utils.go
// AUTHORS:
//     -> Ross Copeland <rhcopeland101@gmail.com>
// WHAT:
// 	-> Random functions that would muddy other files
// */
package main

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
	packagedCandles := make(map[string]Candlestick)
	for coin, candle := range *candlesticks {
		packagedCandles[coin] = *candle
	}
	return &packagedCandles
}
