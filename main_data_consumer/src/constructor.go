package main

/*
	ARGS:
		-> coins (*[]string): the slice of coins
		-> src (int): id of the src of data consumer container (0)
		-> dest (int): destinition id for container
    RETURN:
        -> (*SocketCoinMessage): coin message JSON to be sent to other containers
    WHAT:
		-> Creates messaage to send for coins
*/
func SocketCoinMessageConstruct(coins *[]string, src, dest int) (*SocketCoinMessage){
	return &SocketCoinMessage {
		Type: "coins",
		Msg: *coins,
		Source: src,
		Destination: dest,
	}
}

/*
	ARGS:
		-> msg (string): message being sent
		-> src (int): id of the src of data consumer container (0)
		-> dest (int): destinition id for container
    RETURN:
        -> (*SocketMessage): standard message JSON to be sent to other containers
    WHAT:
		-> Creates standard socket message
*/
func SocketMessageConstruct(msg string, src, dest int) (*SocketMessage) {
	return &SocketMessage {
		Type: "msg",
		Msg: msg,
		Source: src,
		Destination: dest,
	}
}

/*
	ARGS:
		-> price (*CoinPrice):
		-> src (int): id of the src of data consumer container (0)
		-> dest (int): destinition id for container
    RETURN:
        -> (*SocketPriceMessage): 
    WHAT:
		-> Creates price message 
*/
func SocketPriceMessageConstruct(price *CoinPrice, src, dest int) (*SocketPriceMessage) {
	return &SocketPriceMessage {
		Type: "curPrice",
		Msg: *price,
		Source: src,
		Destination: dest,
	}
}

/*
	ARGS:
		-> candle (*Candlestick):
		-> src (int): id of the src of data consumer container (0)
		-> dest (int): destinition id for container
    RETURN:
        -> (*SocketCandleMessage): Pointer to candle object to be sent off
    WHAT:
		-> Creates candle message
*/
func SocketCandleMessageConstruct(candle *Candlestick, src, dest int) (*SocketCandleMessage) {
	return &SocketCandleMessage {
		Type: "candle",
		Msg: *candle,
		Source: src,
		Destination: dest,
	}
}