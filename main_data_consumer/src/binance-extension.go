package main

// import (
// 	"encoding/json"
// 	"fmt"
// 	"strings"
// 	"time"

// 	"github.com/adshao/go-binance"
// 	"github.com/bitly/go-simplejson"
// 	"github.com/gorilla/websocket"
// )

// var (
// 	WebsocketKeepalive = false
// 	WebsocketTimeout   = time.Second * 60
// )

// type WsTradeEvent struct {
// 	Event         string  `json:"e"`
// 	Time          int64   `json:"E"`
// 	Symbol        string  `json:"s"`
// 	TradeID       int64   `json:"t"`
// 	Price         string `json:"p"`
// 	Quantity      string `json:"q"`
// 	BuyerOrderID  int64   `json:"b"`
// 	SellerOrderID int64   `json:"a"`
// 	TradeTime     int64   `json:"T"`
// 	IsBuyerMaker  bool    `json:"m"`
// 	Placeholder   bool    `json:"M"` // add this field to avoid case insensitive unmarshaling
// }

// type RawWsTradeEvent struct {
// 	Data   WsTradeEvent `json:"data"`
// 	Stream string       `json:"string"`
// }

// type WsTradeHandler func(event WsTradeEvent)

// func newWsConfig(endpoint string) *binance.WsConfig {
// 	return &binance.WsConfig{
// 		Endpoint: endpoint,
// 	}
// }

// func newJSON(data []byte) (j *simplejson.Json, err error) {
// 	j, err = simplejson.NewJson(data)
// 	if err != nil {
// 		return nil, err
// 	}
// 	return j, nil
// }

// func keepAlive(c *websocket.Conn, timeout time.Duration) {
// 	ticker := time.NewTicker(timeout)

// 	lastResponse := time.Now()
// 	c.SetPongHandler(func(msg string) error {
// 		lastResponse = time.Now()
// 		return nil
// 	})

// 	go func() {
// 		defer ticker.Stop()
// 		for {
// 			deadline := time.Now().Add(10 * time.Second)
// 			err := c.WriteControl(websocket.PingMessage, []byte{}, deadline)
// 			if err != nil {
// 				return
// 			}
// 			<-ticker.C
// 			if time.Since(lastResponse) > timeout {
// 				c.Close()
// 				return
// 			}
// 		}
// 	}()
// }

// var wsServe = func(cfg *binance.WsConfig, handler binance.WsHandler, errHandler binance.ErrHandler) (doneC, stopC chan struct{}, err error) {
// 	c, _, err := websocket.DefaultDialer.Dial(cfg.Endpoint, nil)
// 	if err != nil {
// 		return nil, nil, err
// 	}
// 	doneC = make(chan struct{})
// 	stopC = make(chan struct{})
// 	go func() {
// 		fmt.Println()
// 		// This function will exit either on error from
// 		// websocket.Conn.ReadMessage or when the stopC channel is
// 		// closed by the client.
// 		defer close(doneC)
// 		if WebsocketKeepalive {
// 			keepAlive(c, WebsocketTimeout)
// 		}
// 		// Wait for the stopC channel to be closed.  We do that in a
// 		// separate goroutine because ReadMessage is a blocking
// 		// operation.
// 		silent := false
// 		go func() {
// 			select {
// 			case <-stopC:
// 				silent = true
// 			case <-doneC:
// 			}
// 			c.Close()
// 		}()
// 		for {
// 			_, message, err := c.ReadMessage()
// 			if err != nil {
// 				if !silent {
// 					errHandler(err)
// 				}
// 				return
// 			}
// 			handler(message)
// 		}
// 	}()
// 	return
// }

// func TradeHandler(message []byte) {

// }

// /*
// 	TODO:
// 		-> perform analytics to see if unmarshalling is the fastest way to do this
// 		-> This should be implemented by the library but oh well, check periodically to see if they have
// */
// func EditedWsCombinedPartialTradeServe(symbols []string, handler WsTradeHandler, errHandler binance.ErrHandler) (doneC, stopC chan struct{}, err error) {
// 	fmt.Println("entered the edited combined trade func")
// 	endpoint := "wss://stream.binance.com:9443/stream?streams="
// 	for _, symbol := range symbols {
// 		endpoint += fmt.Sprintf("%s@trade", strings.ToLower(symbol)) + "/"
// 	}

// 	endpoint = endpoint[:len(endpoint)-1]
// 	cfg := newWsConfig(endpoint)

// 	wsHandler := func(message []byte) {
// 		var raw_event *RawWsTradeEvent = &RawWsTradeEvent{}
// 		err = json.Unmarshal(message, raw_event)

// 		if err != nil {
// 			errHandler(err)
// 			return
// 		}

// 		handler(raw_event.Data)
// 	}
// 	return wsServe(cfg, wsHandler, errHandler)
// }
