package main

import (
	"time"

	coinbasepro "github.com/preichenberger/go-coinbasepro"
	decimal "github.com/shopspring/decimal"
	log "github.com/sirupsen/logrus"
	// "sort"
	// "math"
)

func marketOrder(client *coinbasepro.Client, coin string, amnt decimal.Decimal, buy bool) *coinbasepro.Order {
	product := coin + "-USD"
	var myOrder coinbasepro.Order
	if buy {
		myOrder = coinbasepro.Order{
			Funds:     amnt.String(),
			ProductID: product,
			Side:      "buy",
			Type:      "market",
		}
	} else {
		myOrder = coinbasepro.Order{
			Size:      amnt.String(),
			ProductID: product,
			Side:      "sell",
			Type:      "market",
		}
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
