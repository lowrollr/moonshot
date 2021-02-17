package main

func SocketCoinMessageConstruct(coins *[]string, src, dest int) (*SocketCoinMessage){
	return &SocketCoinMessage {
		Type: "coins",
		Msg: *coins,
		Source: src,
		Destination: dest,
	}
}

func SocketMessageConstruct(msg string, src, dest int) (*SocketMessage) {
	return &SocketMessage {
		Type: "msg",
		Msg: msg,
		Source: src,
		Destination: dest,
	}
}

func SocketPriceMessageConstruct(price *CoinPrice, src, dest int) (*SocketPriceMessage) {
	return &SocketPriceMessage {
		Type: "price",
		Msg: *price,
		Source: src,
		Destination: dest,
	}
}
func SocketCandleMessageConstruct(candle *Candlestick, src, dest int) (*SocketCandleMessage) {
	return &SocketCandleMessage {
		Type: "candle",
		Msg: *candle,
		Source: src,
		Destination: dest,
	}
}