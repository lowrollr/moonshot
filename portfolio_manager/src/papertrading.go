/*
FILE: papertrading.go
AUTHORS:
	-> Jacob Marshall <marshingjay@gmail.com>
WHAT:
	-> Implements all paper trading functionality
*/

package main

import (
	"fmt"
	"strconv"

	decimal "github.com/shopspring/decimal"
	log "github.com/sirupsen/logrus"
)

/*
	RECEIVER:
		-> pm (*PortfolioManager): PortfolioManager object to update
	ARGS:
		-> coin (string): coin to enter a position in
		-> cashAllocaetd (float64): cash allocated to entering this position
		-> targetPrice (float64): last close price of the asset, price we are targeting to enter at (used for calculating slippage)
    RETURN:
        -> cashAllocated (float64): the amount of cash spent to open the resultant position
    WHAT:
		-> simulates opening a position using the live order book
		-> walks down the bid order book until the order is filled
*/
func (pm *PortfolioManager) paperEnter(coin string, cashAllocated float64, targetPrice float64) float64 {
	// calculate the fees paid for entering this position
	fees := cashAllocated * pm.TakerFee

	// keep track of the total amount of the coin we've purchased
	totalAmnt := 0.0

	// calculate the cash available for purchasing after fees
	cashAvailable := cashAllocated - fees

	// keep track of the cash we have left to spend
	cashRemaining := cashAvailable

	// lock the order book, we don't want it to change as we're walking down it
	pm.CoinDict[coin].CoinOrderBook.Lock()

	// get the best order on the order book -- we'll start there
	curOrder := pm.CoinDict[coin].CoinOrderBook.Asks.BestOrder

	// iterate until the position is filled or we reach the end
	for cashRemaining > 0.0 && curOrder != nil {

		// calculate how much it  would cost to purchase everything offered at the current price
		amntToSpend := curOrder.Price * curOrder.Amnt

		// if we have the cash, buy all of it
		if cashRemaining >= amntToSpend {
			cashRemaining -= amntToSpend
			totalAmnt += curOrder.Amnt
		} else {
			// otherwise, spend all our cash on part of it
			// proportion we can afford = casnRemaining / how much is available to buy (amntToSpend)
			proportionOfAmnt := cashRemaining / amntToSpend
			cashRemaining = 0
			totalAmnt += (proportionOfAmnt * curOrder.Amnt)
		}

		// go to the next order
		curOrder = curOrder.Next
	}

	// throw a warning if we hit the end of the order book, that probably shouldn't happen!
	if curOrder == nil {
		log.Warn("WARNING: hit end of bid order book for coin: ", coin)
	}

	// unlock the order book, we are done reading it
	pm.CoinDict[coin].CoinOrderBook.Unlock()

	// update the given coin's CoinInfo object with the trade information if we were able to purchase any of the coin
	info := pm.CoinDict[coin]
	if totalAmnt > 0.0 {
		// update CoinInfo
		info.InPosition = true
		info.CashInvested = cashAllocated
		info.EnterPriceFl = cashAvailable / totalAmnt
		info.AmntOwned = decimal.NewFromFloat(totalAmnt)

		// add the new volume to the PM's running total
		pm.Volume += cashAvailable

		// calculate new fees after volume has been added to the PM's running total
		pm.calcFees()

		// log the entered position and the slippage we incurred
		log.Println("Entered ", coin, ": ", totalAmnt, "@", info.EnterPriceFl)
		slippage := -100.0 * ((info.EnterPriceFl / targetPrice) - 1.0)
		log.Println("Slippage: ", slippage)

		// send a message with the entered position's information to frontend
		sendEnter(pm.FrontendSocket, coin, info.AmntOwned.String(), fmt.Sprintf("%f", info.EnterPriceFl))

		// return the cash we spent on this position
		return cashAllocated
	} else {

		// if no position was taken, no cash was spent -- return 0
		return 0.0
	}
}

/*
	RECEIVER:
		-> pm (*PortfolioManager): PortfolioManager object to update
	ARGS:
		-> coin (string): coin to exit a position in
		-> portionToSell (decimal.Decimal): portion of the position to exit
		-> targetPrice (float64): last close price of the asset, price we are targeting to exit at (used for calculating slippage)
    RETURN:
        -> cashAllocated (float64): the amount of cash received from closing all/part of the position
    WHAT:
		-> simulates closing a position using the live order book
		-> walks up the ask order book until the order is filled
*/
func (pm *PortfolioManager) paperExit(coin string, portionToSell decimal.Decimal, targetPrice float64) float64 {

	// get portionToSell as a float
	amntStr := portionToSell.String()
	amntFlt, _ := strconv.ParseFloat(amntStr, 64)

	// calculate the fees paid for entering this position
	fees := amntFlt * pm.TakerFee

	// keep track of the total amount of cash we've recieved while closing this position
	cashReceived := 0.0

	// calculate the amount of the coin available to sell after fees
	amntAvailable := amntFlt - fees

	// keep track of the amount of the coin we have left to sell
	amntRemaining := amntAvailable

	// lock the order book, we don't want it to change as we're walking up it
	pm.CoinDict[coin].CoinOrderBook.Lock()

	// get the best order on the order book -- we'll start there
	curOrder := pm.CoinDict[coin].CoinOrderBook.Bids.BestOrder

	// iterate until the desired amount of the position is closed, or until we've reached the end
	for amntRemaining > 0.0 && curOrder != nil {
		// if we have enough to sell to all the buyers at this price, do that
		if amntRemaining >= curOrder.Amnt {
			amntRemaining -= curOrder.Amnt
			cashReceived += curOrder.Price * curOrder.Amnt
		} else {
			// otherwise, liquidate the remaining part of the position at the given price
			amntRemaining = 0
			cashReceived += (amntRemaining * curOrder.Price))
		}

		// go to the next order
		curOrder = curOrder.Next
	}

	// throw a warning if we hit the end of the order book, that probably shouldn't happen!
	if curOrder == nil {
		log.Warn("WARNING: hit end of ask order book for coin: ", coin)
	}

	// unlock the order book, we are done reading it
	pm.CoinDict[coin].CoinOrderBook.Unlock()

	// update the given coin's CoinInfo object with the trade information if we were able to liquidate part/all of our position
	info := pm.CoinDict[coin]
	if cashReceived > 0.0 {

		// if we are not selling all of our position, increment IntermediateCash
		if portionToSell != info.AmntOwned {
			info.IntermediateCash += cashReceived
		} else {
			// otherwise, update the profit percentage and other CoinInfo information
			info.InPosition = false
			profitPercentage := ((cashReceived + info.IntermediateCash) / info.CashInvested) - 1.0
			info.IntermediateCash = 0.0
			info.updateProfitInfo(profitPercentage)
		}

		// add the new volume to the PM's running total
		pm.Volume += cashReceived

		// calculate new fees after volume has been added to the PM's running total
		pm.calcFees()

		// calculate the average price we sold the coin for
		averagePrice := cashReceived / amntAvailable

		// log the exited position and the slippage we incurred
		log.Println("Exited ", coin, ": ", amntFlt, "@", averagePrice)
		slippage := 100.0 * ((averagePrice / targetPrice) - 1.0)
		log.Println("Slippage: ", slippage)

		// send a message with the exited position's information to frontend
		sendExit(pm.FrontendSocket, coin, portionToSell.String(), fmt.Sprintf("%f", averagePrice))

		// return the cash we received from liquidation
		return cashReceived
	} else {
		// if we did not liquidate any of our position, we receive no cash
		return 0.0
	}
}

/*
	RECEIVER:
		-> pm (*PortfolioManager): PortfolioManager object to update
	ARGS:
		-> N/A
    RETURN:
        -> N/A
    WHAT:
		-> calculate what fees should be charged on the taker side with the current volume
		-> note: this is only used for paper trading, coinbase handles this IRL
*/
func (pm *PortfolioManager) calcFees() {
	foundTier := false

	// walk down the fee tiers until our volume is less than the threshold
	for amnt, fee := range coinbaseTakerFees {
		if amnt > pm.Volume {
			pm.TakerFee = fee
			foundTier = true
			break
		}
	}
	// if we reached the end, we pay the lowest taker fees, 0.0004
	if !foundTier {
		pm.TakerFee = 0.0004
	}

	return
}
