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

	shortCandleStickData map[string]*OHCLData

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
	Symbol   string `json:"o"`
	Open     string `json:"o"`
	Close    string `json:"c"`
	High     string `json:"h"`
	Low      string `json:"l"`
	Volume   string `json:"v"`
	TradeNum int64  `json:"n"`
}

type SocketMessage struct {
	Msg         string `json:"msg"`
	Source      string `json:"source"`
	Destination string `json:"destination"`
}

type Candlestick struct {
	coin      string
	startTime int32
	open      float32
	high      float32
	low       float32
	close     float32
}

type SocketKlineMessage struct {
	Msg         Candlestick `json:"msg"`
	Source      string      `json:"source"`
	Destination string      `json:"destination"`
}
