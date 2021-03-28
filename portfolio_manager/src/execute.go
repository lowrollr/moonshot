/*
FILE: execute.go
AUTHORS:
	-> Jacob Marshall <marshingjay@gmail.com>
WHAT:
	-> This file contains fucntionality for interfacing with coinbase (at the lowest level) to place orders
*/

package main

import (
	"time"
	"math"
	"fmt"
	coinbasepro "github.com/preichenberger/go-coinbasepro"
	decimal "github.com/shopspring/decimal"
	log "github.com/sirupsen/logrus"
)

/*
	ARGS:
		-> client (*coinbasepro.Client): Coinbase client (we interface with this to place the order)
		-> coin (string): coin to enter/exit a position in
		-> amnt (decimal.Decimal): cash amount to buy, or coin amount to sell
		-> buy (bool): true if buying, false if selling
    RETURN:
        -> &placedOrder (*coinbasepro.Order): Coinbase order object (contains information about the order)
    WHAT:
		-> interfaces with the Coinbase client to place a market order
		-> waits for the order to settle and then returns
*/
func marketOrder(client *coinbasepro.Client, coin string, amnt decimal.Decimal, buy bool, sigDigits int, partial bool) *coinbasepro.Order {

	// construct the ProductID (<coin>USD)
	product := coin + "-USD"

	amntFlt, _ := amnt.Float64()
	//ensure amnt precision is not too high
	if buy || partial {
		factor := float64(10 * sigDigits)
		amntFlt = math.Round(amntFlt*factor)/factor
	}
	
	// construct the appopriate Coinbase order object
	var myOrder coinbasepro.Order
	if buy {
		myOrder = coinbasepro.Order{
			Funds:     fmt.Sprintf("%f", amntFlt),
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

	// place the order
	placedOrder, err := client.CreateOrder(&myOrder)
	orderID := placedOrder.ID

	// if there was an error, log it
	if err != nil {
		log.Println(err)
	} else {
		// if no errors, wait until the order is filled
		log.Println("Waiting for order to fill...")

		for {
			// if the order has been filled, break
			if placedOrder.Settled {
				break
			} else {
				// check if the order is filled
				placedOrder, err = client.GetOrder(orderID)
				if err != nil {
					log.Println(err)
				}
				// wait 1 ms (to not overload on requests to Coinbase)
				log.Println("Waiting...")
				time.Sleep(time.Millisecond * 1)

			}
		}
	}

	// return the order object
	return &placedOrder
}
