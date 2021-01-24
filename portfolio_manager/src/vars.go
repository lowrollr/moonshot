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

	binanceClinet = binance.Client{}
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
