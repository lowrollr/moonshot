/*
FILE: vars.go
AUTHORS:
    -> Ross Copeland <rhcopeland101@gmail.com>
WHAT:
	-> Global variables needed for programs
	-> Right now it is just variables needed for connecting and
		interfacing with the database
*/
package main

import (
	"bufio"
	"net"
	"os"
)

var (
	dbType    = os.Getenv("DBTYPE")
	db_string = os.Getenv("DBTYPEURL") + "://" + os.Getenv("DBUSER") + ":" + os.Getenv("DBPASS") + "@" + os.Getenv("DBNETLOC") + ":" + os.Getenv("DBPORT") + "/" + os.Getenv("DBNAME") + "?sslmode=disable"

	containerToId = map[string]int {
		"main_data_consumer": 0,
		"beverly_hills": 1,
		"portfolio_manager": 2,
		"frontend": 3,
	}
	
	idToContainer = map[int]string{
		0: "main_data_consumer",
		1: "beverly_hills",
		2: "portfolio_manager",
		3: "frontend",
	}

	allClients map[*Client]int
	Dumbo      *dumbo
)

type Client struct {
	// incoming chan string
	outgoing chan string
	reader   *bufio.Reader
	writer   *bufio.Writer
	conn     net.Conn
	start    bool
}

type KlineData struct {
	EndTime  int64  `json:"t"`
	Symbol   string `json:"s"`
	Open     string `json:"o"`
	Close    string `json:"c"`
	High     string `json:"h"`
	Low      string `json:"l"`
	Volume   string `json:"v"`
	TradeNum int64  `json:"n"`
}

type SocketMessage struct {
	Msg         string `json:"msg"`
	Source      int `json:"src"`
	Destination int `json:"dest"`
}

type Candlestick struct {
	Coin      string
	StartTime int32
	Open      float32
	High      float32
	Low       float32
	Close     float32
}

type SocketCandleMessage struct {
	Msg         Candlestick `json:"msg"`
	Source      int      `json:"src"`
	Destination int      `json:"dest"`
}

type CoinPrice struct {
	Coin  string  `json:"coin"`
	Price float32 `json:"price"`
}

type CoinDataMessage struct {
	Msg         CoinPrice `json:"msg"`
	Source      int    `json:"src"`
	Destination int    `json:"dest"`
}
