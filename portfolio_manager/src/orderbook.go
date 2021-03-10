/*
FILE: orderbook.go
AUTHORS:
	-> Jacob Marshall <marshingjay@gmail.com>
WHAT:
	-> This file impelements orderBook functionality such as initialization, updating, and liquidity calculations
*/

package main

import (
	"strconv"
	"sync"

	ws "github.com/gorilla/websocket"
	log "github.com/sirupsen/logrus"
)

// holds bid/ask Book structs
type OrderBook struct {
	sync.Mutex       // multiple routines will be interfacing with the orderBook, locks are necessary to prevent race conditions
	Bids       *Book // bids
	Asks       *Book // asks
}

// holds either bids or asks
// OrderDict map is paired with doubly-linked list of orders
// for O(1) lookups and deletions
// insertions are O(n), but most new orders are created near the top of the linked list, so the complexity of these operations are oftentimes very small
type Book struct {
	IsBids    bool              // true if this Book contains bids, false if contains asks
	OrderDict map[string]*Order // maps order prices to Order objects
	BestOrder *Order            // head of the doubly linked list of Order objects (is the current lowest Ask if Asks, or highest Bid if Bids)
}

// holds a single order object (price/amnt)
// holds pointers to the next/prev orders (this is an element of the doubly linked list that implements the OrderBook)
type Order struct {
	Next  *Order  // pointer to next order (lower priority)
	Prev  *Order  // pointer to prev order (higher priority)
	Price float64 // Price order buys or sells at
	Amnt  float64 // Amnt order buys or sells
}

/*
	ARGS:
		-> bids (*[][]string): list of price, amnt pairs that represents state to initialize orderBook bids with
		-> asks (*[][]string): list of price, amnt pairs that represents state to initialize orderBook asks with
    RETURN:
        -> newBook (*OrderBook): initialized OrderBook object containing up to date orders
    WHAT:
		-> initializes an OrderBook object with initial lists of bid/ask orders
*/
func InitOrderBook(bids *[][]string, asks *[][]string) *OrderBook {
	// create the bid and ask book objects
	askBook := Book{
		IsBids:    false,
		OrderDict: make(map[string]*Order),
		BestOrder: nil,
	}
	bidBook := Book{
		IsBids:    true,
		OrderDict: make(map[string]*Order),
		BestOrder: nil,
	}

	// create a new OrderBook object with the bid & ask Books
	newBook := OrderBook{
		Bids: &bidBook,
		Asks: &askBook,
	}

	// update the bid Book with each price/amnt pair passed
	for _, pair := range *bids {
		price := pair[0]
		amnt := pair[1]
		bidBook.Update(price, amnt)
	}

	// do the same for the ask Book
	for _, pair := range *asks {
		price := pair[0]
		amnt := pair[1]
		askBook.Update(price, amnt)
	}

	// return the initialized OrderBook
	return &newBook
}

/*
	RECEIVER:
		-> book (*Book): orderBook to update with a new/modified order
	ARGS:
		-> price (string): price of order to update
		-> amnt (string): the order needs to be updated to hold this amount
    RETURN:
        -> N/A
    WHAT:
		-> updates the order book with a new order
		-> or modifies a current order on the book
		-> or deletes a current order on the book
*/
func (book *Book) Update(price string, amnt string) {
	// retrieve the current best order (head of LinkedList)
	curOrder := book.BestOrder

	// convert price and amnt to floats
	priceFl, _ := strconv.ParseFloat(price, 64)
	amntFl, _ := strconv.ParseFloat(amnt, 64)

	// if an order at this price already exists on the order book, we need to update it
	if book.OrderDict[price] != nil {
		// if the amount is zero, this means the order has been removed from the book
		if amntFl == 0.0 {

			// remove the order from the book & update prev and next of surrounding nodes
			order := book.OrderDict[price]
			if order.Prev == nil {
				book.BestOrder = order.Next
			} else {
				order.Prev.Next = order.Next
			}
			if order.Next != nil {
				order.Next.Prev = order.Prev
			}
			delete(book.OrderDict, price)

		} else {
			// otherwise, update the order with the new amount
			book.OrderDict[price].Amnt = amntFl
		}
		return
	} else if amntFl == 0.0 {
		// if amount is zero but an order at that price does not exist, that means we are trying to delete an order we do not have on record
		// this means something has gone horribly wrong
		log.Warn("Order book descrepancy (tried to remove order that did not exist). This should never happen!")
		return
	}

	// if there are no orders currently on the book, we need to create a new order and put it on the book as the head
	if curOrder == nil {
		// create a new Order object
		newOrder := Order{
			Next:  nil,
			Prev:  nil,
			Price: priceFl,
			Amnt:  amntFl,
		}
		// set the best order to be this new order
		book.BestOrder = &newOrder

		// update the price -> order map
		book.OrderDict[price] = &newOrder
		return
	}

	// the book is not empty but there is not an order for this price, we'll need to create a new order and put it on the book

	// we'll need to compare orders appropriately for bids vs. asks
	if book.IsBids {
		// iterate until we find the appropriate position for this order
		for curOrder.Next != nil && curOrder.Price > priceFl {
			curOrder = curOrder.Next
		}

		// if we stopped iterating because we reached the end (i.e curOrder.Price is still greater than priceFl)
		//  then put the order at the end of the orderBook
		if curOrder.Price > priceFl {
			// create a new order
			newOrder := Order{
				Next:  nil,
				Prev:  curOrder,
				Price: priceFl,
				Amnt:  amntFl,
			}
			// place the new order after the last order
			curOrder.Next = &newOrder
			book.OrderDict[price] = &newOrder
		} else {
			// if not, place the order between the previous order and the current order

			// create a new order
			newOrder := Order{
				Next:  curOrder,
				Prev:  curOrder.Prev,
				Price: priceFl,
				Amnt:  amntFl,
			}

			// if there is a previous order, set this new order as that order's next order
			if curOrder.Prev != nil {
				curOrder.Prev.Next = &newOrder
			} else {
				// otherwise, this order becomes the head of the LinkedList
				book.BestOrder = &newOrder
			}

			// set the new order as the new previous order for the current order
			curOrder.Prev = &newOrder

			// update the price -> order map
			book.OrderDict[price] = &newOrder
		}

	} else { // (asks)
		// iterate until we find the appropriate position for this order
		for curOrder.Next != nil && curOrder.Price < priceFl {
			curOrder = curOrder.Next
		}

		// if we stopped iterating because we reached the end (i.e curOrder.Price is still less than priceFl)
		//  then put the order at the end of the orderBook
		if curOrder.Price < priceFl {
			// create a new order
			newOrder := Order{
				Next:  nil,
				Prev:  curOrder,
				Price: priceFl,
				Amnt:  amntFl,
			}
			// place the new order after the last order
			curOrder.Next = &newOrder
			book.OrderDict[price] = &newOrder
		} else {
			// if not, place the order between the previous order and the current order

			// create a new order
			newOrder := Order{
				Next:  curOrder,
				Prev:  curOrder.Prev,
				Price: priceFl,
				Amnt:  amntFl,
			}

			// if there is a previous order, set this new order as that order's next order
			if curOrder.Prev != nil {
				curOrder.Prev.Next = &newOrder
			} else {
				// otherwise, this order becomes the head of the LinkedList
				book.BestOrder = &newOrder
			}

			// set the new order as the new previous order for the current order
			curOrder.Prev = &newOrder

			// update the price -> order map
			book.OrderDict[price] = &newOrder
		}
	}
	return
}

/*
	ARGS:
		-> symbols (*[]string): list of coins to get order book updates/snapshots for
    RETURN:
        -> wsConn (*ws.Conn): new Coinbase order book websocket connection
		-> error (error): any error that the coinbase socket throws
    WHAT:
		-> instantiates a websocket connection to the Coinbase order book websocket for the given symbols/coins
*/
func ConnectToCoinbaseOrderBookSocket(symbols *[]string) (*ws.Conn, error) {

	// attempt to connect to the websocket endpoint
	wsConn, _, err := wsDialer.Dial("wss://ws-feed.pro.coinbase.com", nil)

	// return the error if it fails to connect
	if err != nil {
		return nil, err
	}

	// turn each sybmol into the form <symbol>USD
	actual_symbols := []string{}
	for _, sym := range *symbols {
		actual_symbols = append(actual_symbols, sym+"-USD")
	}

	// create the 'subscribe' message body that needs to be sent in order to start receiving data
	subscribe := CoinBaseMessage{
		Type: "subscribe",
		Channels: []MessageChannel{
			MessageChannel{
				Name:       "level2",
				ProductIds: actual_symbols,
			},
		},
	}

	// write the message to the socket
	if err := wsConn.WriteJSON(subscribe); err != nil {
		// if there's an error, return it
		return nil, err
	}

	// otherwise, return the new websocket connection
	return wsConn, nil
}

/*
	ARGS:
		-> isBid (bool): true if book is Bids, false if book is Asks
		-> book (*Book): Book object to calculate liquidity for
		-> closePrice (float64): price to calculate slippage up/down from
		-> targetSlippage (float64): amount of slippage we're willing to allow
    RETURN:
        -> totalLiquidity (float64): the total dollar amount of liquidity on the order book within the given slippage bounds
    WHAT:
		-> calculates how far down/up the order book we have to walk from a given price (closePrice) before we encounter a maximum amount of slippage (targetSlippage)
		-> this tells us a rough estimate of the liquidity on the order book
*/
func getCurrentLiquidity(isBid bool, book *Book, closePrice float64, targetSlippage float64) float64 {
	// initialize totalLiquidity
	totalLiquidity := 0.0

	// if this is a bid order book, we want to see how far down we can walk
	if isBid {
		// calculate the minimum price we'd be willing to buy for based on targetSlippage and the closePrice
		minPrice := closePrice * (1 - targetSlippage)

		// get the head of the order book LinkedList
		curOrder := book.BestOrder

		// iterate until we go below minPrice
		for curOrder != nil {
			curPrice := curOrder.Price
			if curPrice < minPrice {
				// break if curPrice goes below minPrice -- buying at this price would exceed our target slippage amount
				break
			} else {
				// if the price is still above the min price, add the value of this order to the total liquidity
				totalLiquidity += (curOrder.Amnt * curOrder.Price)
				// go to the next order
				curOrder = curOrder.Next
			}
		}
	} else { // if this is an ask order book, we want to see how far up we can walk
		// calculate the maximum price we'd be willing to buy for based on targetSlippage and the closePrice
		maxPrice := closePrice * (1 + targetSlippage)

		// get the head of the order book LinkedList
		curOrder := book.BestOrder

		// iterate until we go above maxPrice
		for curOrder != nil {
			curPrice := curOrder.Price
			if curPrice > maxPrice {
				// break if curPrice goes above minPrice -- buying at this price would exceed our target slippage amount
				break
			} else {
				// if the price is still below the max price, add the value of this order to the total liquidity
				totalLiquidity += (curOrder.Amnt * curOrder.Price)
				// go to the next order
				curOrder = curOrder.Next
			}
		}
	}

	// return the total liqudity on this side of the order book
	return totalLiquidity
}

/*
	RECEIVER:
		-> pm (*PortfolioManager): PortfolioManager object to update
	ARGS:
		-> N/A
    RETURN:
        -> N/A
    WHAT:
		-> gets the current liquidity for the bid/ask sides of the order book for each coin
		-> stores it in each coin's liquidity SMA object
*/
func (pm *PortfolioManager) UpdateLiquidity() {

	// iterate through each coin
	for _, coin := range *pm.Coins {
		// lock the order book so it doesn't change while we are reading it
		pm.CoinDict[coin].CoinOrderBook.Lock()

		// update the bids side liquidity
		pm.CoinDict[coin].BidLiquidity.Update(getCurrentLiquidity(
			true,
			pm.CoinDict[coin].CoinOrderBook.Bids,
			pm.CandleDict[coin].Close,
			pm.TargetSlippage))

		// update the asks side liquidity
		pm.CoinDict[coin].AskLiquidity.Update(getCurrentLiquidity(
			false,
			pm.CoinDict[coin].CoinOrderBook.Asks,
			pm.CandleDict[coin].Close,
			pm.TargetSlippage))

		// we're done reading, unlock the order book
		pm.CoinDict[coin].CoinOrderBook.Unlock()
	}
}
