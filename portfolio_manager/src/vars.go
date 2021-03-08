package main

import (
	"net"
	"net/http"
	"os"
	"sync"
	"time"

	"github.com/jinzhu/gorm"

	ws "github.com/gorilla/websocket"
)

const (
	CONTYPE = "tcp"
)

var (
	apiKey    = os.Getenv("BINANCEAPIKEY")
	secretKey = os.Getenv("BINANCESECRETKEY")
	wsDialer  ws.Dialer
	upgrader  = ws.Upgrader{
		CheckOrigin: func(r *http.Request) bool {
			return true
		},
	}

	Dumbo     *dumbo
	db        *gorm.DB
	dbType    = os.Getenv("DBTYPE")
	db_string = os.Getenv("DBTYPE") + "://" + os.Getenv("DBUSER") + ":" + os.Getenv("DBPASS") + "@" + os.Getenv("DBNETLOC") + ":" + os.Getenv("DBPORT") + "/" + os.Getenv("DBNAME") + "?sslmode=disable"
	dbName    = os.Getenv("DBNAME")

	domainToUrl = map[string]string{
		"main_data_consumer": "main_data_consumer:" + os.Getenv("DATAPORT"),
		"beverly_hills":      "beverly_hills:" + os.Getenv("BEVPORT"),
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

	listenKey = ""

	CONPORT = ":" + string(os.Getenv("SERVERPORT"))

	stratSocket net.Conn

	coinbaseTakerFees = map[float64]float64{
		10000:     0.005,
		50000:     0.0035,
		100000:    0.0025,
		1000000:   0.0020,
		10000000:  0.0018,
		50000000:  0.0015,
		100000000: 0.001,
		300000000: 0.0007,
		500000000: 0.0005,
	}

	coinbaseMakerFees = map[float64]float64{
		10000:     0.005,
		50000:     0.0035,
		100000:    0.0015,
		1000000:   0.0010,
		10000000:  0.0008,
		50000000:  0.0005,
		100000000: 0.0,
		300000000: 0.0,
		500000000: 0.0,
	}
)

type ServerClient struct {
	sync.RWMutex
	conn *ws.Conn
}

type Client struct {
	conn *ws.Conn
}

type SocketMessage struct {
	Type        string `json:"type"`
	Msg         string `json:"msg"`
	Source      int    `json:"src"`
	Destination int    `json:"dest"`
}

type SocketCoinsMessage struct {
	Type        string   `json:"type"`
	Msg         []string `json:"msg"`
	Source      int      `json:"src"`
	Destination int      `json:"dest"`
}

type CandlestickData struct {
	StartTime int     `json:"time"`
	Open      float64 `json:"open"`
	High      float64 `json:"high"`
	Low       float64 `json:"low"`
	Close     float64 `json:"close"`
	Volume    float64 `json:"volume"`
	NumTrades int     `json:"trades"`
}

type SocketCandleMessage struct {
	Type        string                       `json:"type"`
	Msg         map[string][]CandlestickData `json:"msg"`
	Source      int                          `json:"src"`
	Destination int                          `json:"dest"`
}

type SocketSingleCandleMessage struct {
	Type        string                     `json:"type"`
	Msg         map[string]CandlestickData `json:"msg"`
	Source      int                        `json:"src"`
	Destination int                        `json:"dest"`
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

type Trades struct {
	//0 for entry 1 for exit
	TradeType     bool    `gorm:"not null;"`
	coinName      string  `gorm:"-"`
	SizeTrade     float64 `gorm:"Type:real;not null;"`
	ExecutedValue float64 `gorm:"Type:real;not null;"`
	RealizedValue float64 `gorm:"Type:real;not null;"`
	CoinPrice     float64 `gorm:"Type:real;not null;"`
	Fees          float64 `gorm:"Type:real;not null;"`
	Profit        float64 `gorm:"Type:real;"`
	Slippage      float64 `gorm:Type:real;not null;"`
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
	Bids          [][]string       `json:"bids,omitempty"`
	Asks          [][]string       `json:"asks,omitempty"`
	Changes       [][]string       `json:"changes,omitempty"`
	LastSize      string           `json:"last_size"`
	BestBid       string           `json:"best_bid"`
	BestAsk       string           `json:"best_ask"`
	Channels      []MessageChannel `json:"channels"`
	UserID        string           `json:"user_id"`
	ProfileID     string           `json:"profile_id"`
	LastTradeID   int              `json:"last_trade_id"`
}
