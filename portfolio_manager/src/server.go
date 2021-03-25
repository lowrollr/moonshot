package main

import (
	"net/http"
	"os"
	"encoding/json"

	ws "github.com/gorilla/websocket"
	log "github.com/sirupsen/logrus"
)

func (client *ServerClient) Receive() *map[string]json.RawMessage {
	message := WebsocketMessage{}
	err := client.conn.ReadJSON(&message)
	if err != nil {
		log.Warn("Was not able to read json data from socket because", err)
	}
	return &message.Content
}

func NewServerClient(connection *ws.Conn) *ServerClient {
	serverClient := &ServerClient{
		conn: connection,
	}
	return serverClient
}

func (client *ServerClient) SetConn(conn *ws.Conn) {
	client.Lock()
	client.conn = conn
	client.Unlock()
}

func (client *ServerClient) GetConn() *ws.Conn {
	client.RLock()
	defer client.RUnlock()
	return client.conn
}

//pm specific
func (pm *PortfolioManager) StartServer() {
	http.HandleFunc("/", pm.HandleConnections)
	err := http.ListenAndServe(":"+string(os.Getenv("PM_PORT")), nil)
	if err != nil {
		log.Fatal("ListenAndServe: ", err)
	}
}
func (client *ServerClient) handleFrontendPing(pm *PortfolioManager) {
	for {
		
		messageContent := *client.Receive()
		
		if _, ok := messageContent["ping"]; ok {
			msgContent := make(map[string]interface{})
			client.Lock()
			if pm.IsPaperTrading {
				
				msgContent["portfolio_value"] = pm.PortfolioValue
				pongMsg := WebsocketMessage{
					Content:	 *InterfaceToRawJSON(&msgContent),
					Source:      containerToId["portfolio_manager"],
					Destination: containerToId["frontend"]}
				
				client.conn.WriteJSON(pongMsg)
			} else {
				msgContent["pong"] = true
				pongMsg := WebsocketMessage{
					Content: 	*InterfaceToRawJSON(&msgContent),
					Source:      containerToId["portfolio_manager"],
					Destination: containerToId["frontend"]}
				
				client.conn.WriteJSON(pongMsg)
			}

			client.Unlock()

		} else {
			log.Warn("Invalid message received from frontend")
		}
		
	}
}

func (pm *PortfolioManager) HandleConnections(w http.ResponseWriter, r *http.Request) {
	ws, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		log.Warn("error %v", err)
	}
	message := WebsocketMessage{}
	ws.ReadJSON(&message)
	if _, ok := message.Content["ready"]; ok {
		if idToContainer[message.Source] == "frontend" {
			pm.FrontendSocket = NewServerClient(ws)
			go pm.FrontendSocket.handleFrontendPing(pm)
		}
	}
}
