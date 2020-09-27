package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"

	"github.com/gorilla/mux"
)

func hello(w http.ResponseWriter, req *http.Request) {
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(webError{Msg: "Hello World!"})
}

func main() {
	fmt.Println("Connectting to database")
	//Here going to connect to database
	var err error = nil

	db, err := Dumbo.connectDB(db_string)
	if err != nil {
		panic(err)
	}
	fmt.Println("Connected to database successfully")

	fmt.Println("Creating tables in database")
	err = Dumbo.autoMigrate(db)
	if err != nil {
		panic(err)
	}
	fmt.Println("Adding pre-processed stock data")
	read_store_ticker_name()
	read_store_enumerated()

	fmt.Println("Created tables successfully")
	//create unique constraint
	err = Dumbo.addConstraint(db)
	if err != nil {
		panic(err)
	}

	fmt.Println("Creating HTTP Server ...")
	back_end_server := mux.NewRouter()
	fmt.Println("HTTP Server Created")

	fmt.Println("Creating all API routes")
	back_end_server.HandleFunc("/debug", hello).Methods(http.MethodGet)
	back_end_server.HandleFunc("/getTickerNames", getTickerNames).Methods(http.MethodGet)
	back_end_server.HandleFunc("/getEnumeratedNames", getEnumeratedNames).Methods(http.MethodGet)
	back_end_server.HandleFunc("/testFillDB", testFillDB).Methods(http.MethodGet)

	back_end_server.HandleFunc("/stock_store", stock_store).Methods(http.MethodPost)
	back_end_server.HandleFunc("/multiple_stock_store", multiple_stock_store).Methods(http.MethodPost)
	back_end_server.HandleFunc("/multiple_sentiment_store", multiple_sentiment_store).Methods(http.MethodPost)
	back_end_server.HandleFunc("/sentiment_store", sentiment_store).Methods(http.MethodPost)
	back_end_server.HandleFunc("/check_availibility", check_availibility).Methods(http.MethodPost)
	back_end_server.HandleFunc("/all_data_ml", all_data_ml).Methods(http.MethodPost)
	
	fmt.Println("Start up server")
	addr := "0.0.0.0:7734"
	log.Fatal(http.ListenAndServe(addr, back_end_server))
}