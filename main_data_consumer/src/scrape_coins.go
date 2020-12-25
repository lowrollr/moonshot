/*
FILE: scrape_coins.go
AUTHORS:
    -> Ross Copeland <rhcopeland101@gmail.com>
WHAT:
	-> Inserting coins dynamically into database scraped from website on popularity
*/
package main

import (
	"fmt"
	"strconv"
	"strings"

	"github.com/anaskhan96/soup"
)

/*
	ARGS:
        -> N/A
    RETURN:
        -> ([]CoinData): slice of coin data parsed from website
    WHAT:
		-> This gets coin data from website to dynamically get most popular coins in order
    TODO:
		-> Go through multiple pages, instead of just first page (most popular)
*/
func scrapeWebsite() []CoinData {
	resp, err := soup.Get(scrape_url)
	if err != nil {
		fmt.Println("Could not reach the coinomarketcap.com website")
		panic(err)
	}
	doc := soup.HTMLParse(resp)
	fmt.Println(doc.Text())
	table := doc.Find("tbody")

	rows := table.FindAll("tr")

	var coin_data []CoinData

	for _, row := range rows {
		attr := row.FindAll("td")

		priority_str := attr[0].FullText()
		priority_int, err := strconv.ParseInt(priority_str, 10, 0)
		if err != nil {
			fmt.Println("Could not parse int of this: " + priority_str)
		}
		coin_data = append(coin_data, CoinData{Priority: uint8(priority_int), Name: attr[1].FullText(), 
			Abbr: strings.ToUpper(attr[2].FullText())})
	}
	return coin_data
}

/*
	ARGS:
        -> N/A
    RETURN:
        -> N/A
    WHAT:
		-> Scrapes and stores coin name and abrvs
    TODO:
		-> Get more than just the first 200 on first page
*/
func StorePopularCoins() {
	//get all coin names and abrev
	scraped_data := scrapeWebsite()

	//Delete any entries that are there
	err := Dumbo.deleteCoinIndex()
	if err != nil {
		fmt.Println("Could not delete entries: " + err.Error())
	}

	//store all coin names and abrev
	err = Dumbo.storeScraped(&scraped_data)
	if err != nil {
		fmt.Println(err.Error())
	}
}
