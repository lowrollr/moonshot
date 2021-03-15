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
	"encoding/json"
	"net/http"
	"os"
	"sync"
	"time"

	ws "github.com/gorilla/websocket"
)

var (
	dbType    = os.Getenv("DBTYPE")
	db_string = os.Getenv("DBTYPEURL") + "://" + os.Getenv("DBUSER") + ":" + os.Getenv("DBPASS") + "@" + os.Getenv("DBNETLOC") + ":" + os.Getenv("DBPORT") + "/" + os.Getenv("DBNAME") + "?sslmode=disable"
	wsDialer  ws.Dialer
	upgrader  = ws.Upgrader{
		CheckOrigin: func(r *http.Request) bool {
			return true
		},
	}

	containerToId = map[string]int{
		"main_data_consumer": 0,
		"beverly_hills":      1,
		"portfolio_manager":  2,
		"frontend":           3,
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
	sync.RWMutex
	Conn     *ws.Conn
	ClientId int
}

type SocketCandleMessage struct {
	Type        string      `json:"type"`
	Msg         Candlestick `json:"msg"`
	Source      int         `json:"src"`
	Destination int         `json:"dest"`
}

type SocketByteMessage struct {
	Type        string `json:"type"`
	Msg         []byte `json:"msg"`
	Source      int    `json:"src"`
	Destination int    `json:"dest"`
}

type SocketAllCandleMessage struct {
	Type        string                   `json:"type"`
	Msg         map[string][]Candlestick `json:"msg"`
	Source      int                      `json:"src"`
	Destination int                      `json:"dest"`
}

type CoinPrice struct {
	Coin  string  `json:"coin"`
	Price float64 `json:"price"`
	Time  int64   `json:"time"`
}

type SocketPriceMessage struct {
	Type        string    `json:"type"`
	Msg         CoinPrice `json:"msg"`
	Source      int       `json:"src"`
	Destination int       `json:"dest"`
}

type SocketMessage struct {
	Type        string `json:"type"`
	Msg         string `json:"msg"`
	Source      int    `json:"src"`
	Destination int    `json:"dest"`
}

type SocketCoinMessage struct {
	Type        string   `json:"type"`
	Msg         []string `json:"msg"`
	Source      int      `json:"src"`
	Destination int      `json:"dest"`
}

type SocketAllDataMessage struct {
	Type        string                   `json:"type"`
	Msg         map[string][]Candlestick `json:"msg"`
	Source      int                      `json:"src"`
	Destination int                      `json:"dest"`
}

type SocketPMDataMessage struct {
	Type        string           `json:"type"`
	Msg         TradesAndCandles `json:"msg"`
	Source      int              `json:"src"`
	Destination int              `json:"dest"`
	Error       string           `json:"error"`
}

type TradesAndCandles struct {
	TradeHistory map[string][]Trades      `json:"trade_history"`
	Profits      map[string][]float64     `json:"profits"`
	Coins        map[string][]Candlestick `json:"candles"`
}

//coinbase vars
type CoinBaseMessage struct {
	Type          string           `json:"type"`
	ProductID     string           `json:"product_id"`
	ProductIds    []string         `json:"product_ids"`
	TradeID       int              `json:"trade_id,number"`
	OrderID       string           `json:"order_id"`
	ClientOID     string           `json:"client_oid"`
	Sequence      int64            `json:"sequence,number"`
	MakerOrderID  string           `json:"maker_order_id"`
	TakerOrderID  string           `json:"taker_order_id"`
	Time          time.Time        `json:"time,string"`
	RemainingSize string           `json:"remaining_size"`
	NewSize       string           `json:"new_size"`
	OldSize       string           `json:"old_size"`
	Size          string           `json:"size"`
	Price         string           `json:"price"`
	Side          string           `json:"side"`
	Reason        string           `json:"reason"`
	OrderType     string           `json:"order_type"`
	Funds         string           `json:"funds"`
	NewFunds      string           `json:"new_funds"`
	OldFunds      string           `json:"old_funds"`
	Message       string           `json:"message"`
	Bids          []SnapshotEntry  `json:"bids,omitempty"`
	Asks          []SnapshotEntry  `json:"asks,omitempty"`
	Changes       []SnapshotChange `json:"changes,omitempty"`
	LastSize      string           `json:"last_size"`
	BestBid       string           `json:"best_bid"`
	BestAsk       string           `json:"best_ask"`
	Channels      []MessageChannel `json:"channels"`
	UserID        string           `json:"user_id"`
	ProfileID     string           `json:"profile_id"`
	LastTradeID   int              `json:"last_trade_id"`
}

type MessageChannel struct {
	Name       string   `json:"name"`
	ProductIds []string `json:"product_ids"`
}

type SnapshotChange struct {
	Side  string
	Price string
	Size  string
}

type SnapshotEntry struct {
	Price string
	Size  string
}

type SignedMessage struct {
	CoinBaseMessage
	Key        string `json:"key"`
	Passphrase string `json:"passphrase"`
	Timestamp  string `json:"timestamp"`
	Signature  string `json:"signature"`
}

func (e *SnapshotEntry) UnmarshalJSON(data []byte) error {
	var entry []string

	if err := json.Unmarshal(data, &entry); err != nil {
		return err
	}

	e.Price = entry[0]
	e.Size = entry[1]

	return nil
}

func (e *SnapshotChange) UnmarshalJSON(data []byte) error {
	var entry []string

	if err := json.Unmarshal(data, &entry); err != nil {
		return err
	}

	e.Side = entry[0]
	e.Price = entry[1]
	e.Size = entry[2]

	return nil
}
