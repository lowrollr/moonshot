package main

import (
	"net/http"
	"os"

	ws "github.com/gorilla/websocket"
	log "github.com/sirupsen/logrus"
)

func (client *ServerClient) Receive() string {
	message := &SocketMessage{}
	err := client.conn.ReadJSON(message)

	if err != nil {
		if err.Error() == "EOF" {
			return ""
		}
		log.Warn("Not able to read data type: " + err.Error())
	}
	return message.Msg
}

func NewServerClient(connection *ws.Conn) *ServerClient {
	serverClient := &ServerClient{
		conn: connection,
	}
	return serverClient
}

func (client *ServerClient) ReceiveInit() bool {
	message := &SocketMessage{}
	err := client.GetConn().ReadJSON(message)
	if err != nil {
		log.Warn("Was not able to read init message because", err)
	}
	if message.Type == "init" {
		return true
	}
	return false
}

func (client *ServerClient) SetConn(conn *ws.Conn) {
	client.Lock()
	log.Println(client.conn)
	log.Println(conn)
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
func (client *ServerClient) handleFrontendPing() {
	for {
		message := SocketMessage{}
		err := client.conn.ReadJSON(&message)
		if err == nil {
			if message.Type == "ping" {
				client.Lock()
				pongMsg := SocketMessage{
					Msg:         "fuck you too",
					Type:        "pong",
					Source:      containerToId["portfolio_manager"],
					Destination: containerToId["frontend"]}

				client.conn.WriteJSON(pongMsg)
				client.Unlock()

			} else {
				log.Warn("Invalid message received from frontend")
			}
		} else {
			log.Warn("Error reading frontend socket")
		}
	}
}

func (pm *PortfolioManager) HandleConnections(w http.ResponseWriter, r *http.Request) {
	ws, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		log.Warn("error %v", err)
	}
	message := SocketMessage{}
	err = ws.ReadJSON(&message)
	if message.Type == "start" {
		if idToContainer[message.Source] == "frontend" {
			pm.FrontendSocket = NewServerClient(ws)
			go pm.FrontendSocket.handleFrontendPing()
		} else {
			log.Warn("Wrong source sent, source sent:", idToContainer[message.Source])
		}
	} else if message.Type == "init" {
		if idToContainer[message.Source] == "frontend" {
			pm.FrontendSocket.SetConn(ws)

		} else {
			log.Warn("Wrong source sent, source sent:", idToContainer[message.Source])
		}
	} else {
		log.Warn("Wrong msg type send, type sent:", message.Type)
	}
	return
}
