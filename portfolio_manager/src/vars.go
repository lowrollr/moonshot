package main

import (
	"bufio"
	"net"
	"os"

	"github.com/ross-hugo/go-binance/v2"
)

const (
	CONTYPE = "tcp"
)

var (
	apiKey    = os.Getenv("BINANCEAPIKEY")
	secretKey = os.Getenv("BINANCESECRETKEY")

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

	binanceClient = binance.Client{}
	listenKey     = ""

	CONPORT = ":" + string(os.Getenv("SERVERPORT"))

	stratSocket net.Conn
)

type ServerClient struct {
	// incoming chan string
	outgoing chan string
	reader   *bufio.Reader
	writer   *bufio.Writer
	conn     *net.Conn
}

type Client struct {
	outgoing chan string
	reader   *bufio.Reader
	writer   *bufio.Writer
	conn     net.Conn
}

type SocketMessage struct {
	Msg         string `json:"msg"`
	Source      int    `json:"src"`
	Destination int    `json:"dest"`
}

type CandlestickData struct {
	time   int32
	close  float32
	open   float32
	high   float32
	low    float32
	volume float32
	trades int32
}
