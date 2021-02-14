package main

import (
	"time"

	coinbasepro "github.com/preichenberger/go-coinbasepro"
	decimal "github.com/shopspring/decimal"
	log "github.com/sirupsen/logrus"
	// "sort"
	// "math"
)

func marketOrder(client *coinbasepro.Client, coin string, amnt float32, buy bool) *coinbasepro.Order {
	side := "sell"
	if buy {
		side = "buy"
	}
	product := coin + "-USD"
	myOrder := coinbasepro.Order{
		Funds:     decimal.NewFromFloat(float64(amnt)).String(),
		ProductID: product,
		Side:      side,
		Type:      "market",
	}
	placedOrder, err := client.CreateOrder(&myOrder)
	orderID := placedOrder.ID
	if err != nil {
		log.Println(err)
	} else {
		log.Println("Waiting for order to fill...")

		for {
			if placedOrder.Settled {
				break
			} else {

				placedOrder, err = client.GetOrder(orderID)
				if err != nil {
					log.Println(err)
				}
				log.Println("Waiting...")
				time.Sleep(time.Millisecond * 1)

			}
		}
	}

	return &placedOrder
}
