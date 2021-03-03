package main

import (
	"strconv"
	"time"

	ws "github.com/gorilla/websocket"
	log "github.com/sirupsen/logrus"
)

func (client *Client) Receive() string {
	message := SocketMessage{}
	err := client.conn.ReadJSON(&message)
	if err != nil {
		log.Warn("Was not able to read json data from socket because", err)
	}
	return message.Msg
}

func (client *Client) ReceiveSingleCandleData() *map[string]CandlestickData {
	message := SocketSingleCandleMessage{}

	err := client.conn.ReadJSON(&message)
	if err != nil {
		log.Warn("Was not able to read json data from socket because", err)
	}

	return &message.Msg
}

func (client *Client) ReceiveCandleData() *map[string][]CandlestickData {
	message := SocketCandleMessage{}

	err := client.conn.ReadJSON(&message)
	if err != nil {
		log.Warn("Was not able to read json data from socket because", err)
	}

	return &message.Msg
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

func StartClient() map[string]*Client {
	mapDomainConnection := make(map[string]*Client)
	for hostname, fullUrl := range domainToUrl {
		mapDomainConnection[fullUrl] = NewInternalClient(ConnectServer(fullUrl))
		if hostname == "beverly_hills" {
			StartInit(mapDomainConnection[fullUrl])
		}
	}
	return mapDomainConnection
}

func (client *Client) StartRemoteServer(dest string) {
	startMessage := SocketMessage{Msg: "",
		Type:        "start",
		Source:      containerToId["portfolio_manager"],
		Destination: containerToId[dest]}

	for {
		err := client.conn.WriteJSON(startMessage)
		if err != nil {
			log.Warn("Was not able to connect/write to", dest)
			time.Sleep(time.Second * 3)
		} else {
			return
		}
	}
}

func StartInit(bevConn *Client) {
	initMsg := SocketMessage{Msg: "",
		Type:        "init",
		Source:      containerToId["portfolio_manager"],
		Destination: containerToId["beverly_hills"]}
	err := bevConn.conn.WriteJSON(initMsg)

	if err != nil {
		log.Panic("Was not able to send init message to beverly hills", err)
	}
}

func sendEnter(frontendConn *ServerClient, coin string, amnt string, price string) {
	frontendConn.RLock()
	msg := SocketMessage{
		Msg:         coin + "," + amnt + "," + price,
		Type:        "enter",
		Source:      containerToId["portfolio_manager"],
		Destination: containerToId["frontend"]}
	err := frontendConn.conn.WriteJSON(msg)
	if err != nil {
		log.Panic("Error sending enter msg to Frontend")
	}
	frontendConn.RUnlock()
}

func sendExit(frontendConn *ServerClient, coin string, amnt string, price string) {
	frontendConn.RLock()
	msg := SocketMessage{
		Msg:         coin + "," + amnt + "," + price,
		Type:        "exit",
		Source:      containerToId["portfolio_manager"],
		Destination: containerToId["frontend"]}
	err := frontendConn.conn.WriteJSON(msg)
	if err != nil {
		log.Panic("Error sending exit msg to Frontend")
	}
	frontendConn.RUnlock()
}

func GetPrediction(bevConn *Client, coin string, timestamp int) bool {
	msg := SocketMessage{
		Msg:         coin + "," + strconv.Itoa(timestamp),
		Type:        "predict",
		Source:      containerToId["portfolio_manager"],
		Destination: containerToId["beverly_hills"],
	}
	err := bevConn.conn.WriteJSON(msg)
	if err != nil {
		log.Warn("Error sending predict message to Beverly Hills")
	}
	response := SocketMessage{}

	err = bevConn.conn.ReadJSON(&response)
	if err == nil {
		if response.Type == "prediction" {
			result, _ := strconv.ParseBool(response.Msg)
			return result
		} else {
			log.Warn("Error: BH sent incorrect message type when asked for prediction!")
		}
	}
	return false
}

func (client *Client) GetPreviousData(dest string) (*[]string, *map[string][]CandlestickData) {
	if dest != "main_data_consumer" {
		log.Warn("dont try and get coins from something thats not main data consumer")
	}
	dataMessage := SocketMessage {
		Msg: "150",
		Type: "data",
		Source: containerToId["portfolio_manager"],
		Destination: containerToId[dest],
	}
	for {
		err := client.conn.WriteJSON(dataMessage)
		if err != nil {
			log.Warn("Was not able to send data message to", dest, ". With error:", err)
		}
		candle_data := client.ReceiveCandleData()
		coin_labels := make([]string, len(*candle_data))

		i := 0
		for coin, _ := range *candle_data {
			coin_labels[i] = coin
			i++
		}
		return &coin_labels, candle_data
	}
}

func (client *Client) GetCoins(dest string) *[]string {
	if dest != "main_data_consumer" {
		log.Warn("dont try and get coins from something thats not main data consumer")
	}
	coinKeyWord := SocketMessage{Msg: "",
		Type:        "coins",
		Source:      containerToId["portfolio_manager"],
		Destination: containerToId["main_data_consumer"]}
	for {
		err := client.conn.WriteJSON(coinKeyWord)
		if err != nil {
			log.Warn("Was not able to send coin message to data consumer", err)
		}
		message := SocketCoinsMessage{}
		err = client.conn.ReadJSON(&message)

		if err == nil {
			// noHeaderMsg, messageType := ParseMessage(&response)
			if message.Type == "coins" {
				return &message.Msg
			} else {
				log.Panic("Did not send the correct message type")
			}
		} else {
			log.Warn("Could not get coins from DC because", err)
		}
		log.Println("Could not get coins from main data consumer. Trying again... ")
		time.Sleep(3 * time.Second)
	}
}
