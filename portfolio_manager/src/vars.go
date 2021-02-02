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
	conn     net.Conn
}

type Client struct {
	outgoing chan string
	reader   *bufio.Reader
	writer   *bufio.Writer
	conn     net.Conn
}

type webError struct {
	Msg string `json:"msg"`
}

type CryptoPayload struct {
	//this is data we get from Kraken. Dunno what to put here
}

type SocketMessage struct {
	Msg         string `json:"msg"`
	Source      string `json:"source"`
	Destination string `json:"destination"`
}
