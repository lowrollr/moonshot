package main

import (
	"time"
	"encoding/json"

	ws "github.com/gorilla/websocket"
	log "github.com/sirupsen/logrus"
	decimal "github.com/shopspring/decimal"
)

func (client *Client) Receive() *map[string]json.RawMessage {
	message := WebsocketMessage{}
	err := client.conn.ReadJSON(&message)
	if err != nil {
		log.Warn("Was not able to read json data from socket because", err)
	}
	return &message.Content
}


func NewInternalClient(connection *ws.Conn) *Client {
	client := &Client{
		conn: connection,
	}
	return client
}

func ConnectServer(dest string) *ws.Conn {
	for {
		conn, _, err := wsDialer.Dial("ws://"+dest, nil)
		if err == nil {
			log.Println("Connected to ", dest)
			return conn
		}
		log.Printf("Could not connect to the %s with error: %s Retrying...", dest, err.Error())
		time.Sleep(time.Second * 3)
	}
}

func StartClients() map[string]*Client {
	mapDomainConnection := make(map[string]*Client)
	for _, fullUrl := range domainToUrl {
		mapDomainConnection[fullUrl] = NewInternalClient(ConnectServer(fullUrl))
	}
	return mapDomainConnection
}

func sendEnter(frontendConn *ServerClient, coin string, amnt string, price string) {
	
	
	msgContent := make(map[string]interface{})
	msgContent["enter"] = make(map[string]interface{})
	enterContent := msgContent["enter"].(map[string]interface{})
	enterContent["coin"] = coin
	enterContent["amnt"] = amnt
	enterContent["price"] = price
	frontendConn.RLock()
	msg := WebsocketMessage{
		Content:     *InterfaceToRawJSON(&msgContent),
		Source:      containerToId["portfolio_manager"],
		Destination: containerToId["frontend"]}
	
	err := frontendConn.conn.WriteJSON(msg)
	if err != nil {
		log.Panic("Error sending enter msg to Frontend")
	}
	frontendConn.RUnlock()
}

func sendExit(frontendConn *ServerClient, coin string, amnt string, price string) {
	msgContent := make(map[string]interface{})
	msgContent["exit"] = make(map[string]interface{})
	exitContent := msgContent["exit"].(map[string]interface{})
	exitContent["coin"] = coin
	exitContent["amnt"] = amnt
	exitContent["price"] = price
	frontendConn.RLock()
	
	msg := WebsocketMessage{
		Content:     *InterfaceToRawJSON(&msgContent),
		Source:      containerToId["portfolio_manager"],
		Destination: containerToId["frontend"]}
	
	err := frontendConn.conn.WriteJSON(msg)
	if err != nil {
		log.Panic("Error sending exit msg to Frontend")
	}
	frontendConn.RUnlock()
}

func GetPrediction(bevConn *Client, coin string, timestamp int) bool {
	msgContent := make(map[string]interface{})
	msgContent["predict"] = make(map[string]interface{})
	predictContent := msgContent["predict"].(map[string]interface{})
	predictContent["coin"] = coin
	predictContent["timestamp"] = timestamp

	msg := WebsocketMessage{
		Content:     *InterfaceToRawJSON(&msgContent),
		Source:      containerToId["portfolio_manager"],
		Destination: containerToId["frontend"]}
	
	err := bevConn.conn.WriteJSON(msg)
	if err != nil {
		log.Warn("Error sending predict message to Beverly Hills")
	}

	responseContent := *bevConn.Receive()
	if err == nil {
		if result, ok := responseContent["prediction"]; ok{
			var resultBool bool
			err := json.Unmarshal(result, &resultBool)
			if err != nil {
				log.Panic("Error unmarshaling prediction")
			}
			return resultBool
		} else {
			log.Warn("Error: BH sent incorrect message content when asked for prediction!")
		}
	}
	return false
}

func (client *Client) GetPreviousData(dest string, numTrades int) (*[]string, *map[string][]Trade, *map[string][]Candlestick, *map[string][]float64) {
	
	msgContent := make(map[string]interface{})
	msgContent["coins"] = true
	msgContent["trade_profits"] = numTrades
	msgContent["candles"] = 150
	msgContent["open_trades"] = true

	msg := WebsocketMessage{
		Content:	 *InterfaceToRawJSON(&msgContent),
		Source:      containerToId["portfolio_manager"],
		Destination: containerToId[dest],
	}
	
	
	err := client.conn.WriteJSON(msg)
	if err != nil {
		log.Warn("Was not able to send data message to", dest, ". With error:", err)
	} 
	responseContent := *client.Receive()

	
	var coins []string
	err = json.Unmarshal(responseContent["coins"], &coins)
	if err != nil {
		log.Panic("Error unmarshaling coins message content")
	}

	var tempTrades map[string][]ExactTrade
	err = json.Unmarshal(responseContent["open_trades"], &tempTrades)
	if err != nil {
		log.Panic("Error unmarshaling open_trades message content")
	}
	var openTrades map[string][]Trade
	for key, trades := range tempTrades {
		openTrades[key] = make([]Trade, len(trades))
		for index, trade := range trades{
			decUnits, _ := decimal.NewFromString(trade.Units)
			decEV, _ := decimal.NewFromString(trade.ExecutedValue)
			flUnits, _ := decUnits.Float64()
			flEV, _ := decEV.Float64()
			openTrades[key][index] = Trade{
				TypeId: trade.TypeId,
				coinName: key,
				Units: flUnits,
				ExecutedValue: flEV,
				Fees: trade.Fees,
				Profit: trade.Profit,
				Slippage: trade.Slippage,
				Timestamp: trade.Timestamp,
			}
		}
	}

	var candles map[string][]Candlestick
	err = json.Unmarshal(responseContent["candles"], &candles)
	if err != nil {
		log.Panic("Error unmarshaling candles message content")
	}

	var tradeProfits map[string][]float64
	err = json.Unmarshal(responseContent["trade_profits"], &tradeProfits)
	if err != nil {
		log.Panic("Error unmarshaling trade_profits message content")
	}
	
	return &coins, &openTrades, &candles, &tradeProfits
	
}

func (client *Client) SendReadyMsg(dest string) {
	msgContent := make(map[string]interface{})
	msgContent["ready"] = true
	msg := WebsocketMessage {
		Content: *InterfaceToRawJSON(&msgContent),
		Source:      containerToId["portfolio_manager"],
		Destination: containerToId[dest],
	}
	
	err := client.conn.WriteJSON(msg)
	if err != nil {
		log.Warn("Was not able to send data message to", dest, ". With error:", err)
	} 
}

func InterfaceToRawJSON(inter *map[string]interface{}) *map[string]json.RawMessage {
	rawJSONMap := make(map[string]json.RawMessage)
	for key, val := range *inter {
		valJSON, err := json.Marshal(&val)
		if err != nil {
			log.Panic("Could not marshal json: ", val)
		} else {
			rawJSONMap[key] = valJSON
		}
	}
	

	return &rawJSONMap
}