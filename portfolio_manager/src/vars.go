package main

import (
	"net"
	"net/http"
	"os"
	"sync"

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
)

type ServerClient struct {
	sync.RWMutex
	conn *ws.Conn
}

type Client struct {
	conn *ws.Conn
}

type CryptoPayload struct {
	//this is data we get from Kraken. Dunno what to put here
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
