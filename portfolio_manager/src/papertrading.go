package main

import (
	"fmt"
	"strconv"

	decimal "github.com/shopspring/decimal"
	log "github.com/sirupsen/logrus"
)

func (pm *PortfolioManager) paperEnter(coin string, cashAllocated float64, targetPrice float64) float64 {
	fees := cashAllocated * pm.PaperInfo.TakerFee
	totalAmnt := 0.0
	cashAvailable := cashAllocated - fees
	cashRemaining := cashAvailable
	pm.CoinDict[coin].CoinOrderBook.Lock()

	curOrder := pm.CoinDict[coin].CoinOrderBook.Asks.BestOrder
	for cashRemaining > 0.0 && curOrder != nil {
		amntToSpend := curOrder.Price * curOrder.Amnt
		if cashRemaining >= amntToSpend {
			cashRemaining -= amntToSpend
			totalAmnt += curOrder.Amnt
		} else {
			proportionOfAmnt := cashRemaining / amntToSpend
			cashRemaining = 0
			totalAmnt += (proportionOfAmnt * curOrder.Amnt)
		}
		curOrder = curOrder.Next
	}

	pm.CoinDict[coin].CoinOrderBook.Unlock()

	info := pm.CoinDict[coin]
	if totalAmnt > 0.0 {
		info.InPosition = true
		info.CashInvested = cashAllocated
		info.EnterPriceFl = cashAvailable / totalAmnt
		info.AmntOwned = decimal.NewFromFloat(totalAmnt)
		pm.PaperInfo.Volume += cashAvailable
		pm.calcFees()
		log.Println("Entered ", coin, ": ", totalAmnt, "@", info.EnterPriceFl)
		slippage := -100.0 * ((info.EnterPriceFl / targetPrice) - 1.0)
		log.Println("Slippage: ", slippage)
		sendEnter(pm.FrontendSocket, coin, info.AmntOwned.String(), fmt.Sprintf("%f", info.EnterPriceFl))
		return cashAllocated
	} else {
		return 0.0
	}
}

func (pm *PortfolioManager) paperExit(coin string, portionToSell decimal.Decimal, targetPrice float64) float64 {

	amntStr := portionToSell.String()
	amntFlt, _ := strconv.ParseFloat(amntStr, 64)

	fees := amntFlt * pm.PaperInfo.TakerFee
	cashReceived := 0.0
	amntAvailable := amntFlt - fees
	amntRemaining := amntAvailable
	pm.CoinDict[coin].CoinOrderBook.Lock()

	curOrder := pm.CoinDict[coin].CoinOrderBook.Bids.BestOrder
	for amntRemaining > 0.0 && curOrder != nil {

		if amntRemaining >= curOrder.Amnt {
			amntRemaining -= curOrder.Amnt
			cashReceived += curOrder.Price * curOrder.Amnt
		} else {
			proportionOfAmnt := amntRemaining / curOrder.Amnt
			amntRemaining = 0
			cashReceived += (proportionOfAmnt * (curOrder.Amnt * curOrder.Price))
		}
		curOrder = curOrder.Next
	}

	pm.CoinDict[coin].CoinOrderBook.Unlock()

	info := pm.CoinDict[coin]
	if cashReceived > 0.0 {
		if portionToSell != info.AmntOwned {
			info.IntermediateCash += cashReceived
		} else {
			info.InPosition = false
			profitPercentage := ((cashReceived + info.IntermediateCash) / info.CashInvested) - 1.0
			info.IntermediateCash = 0.0
			info.updateProfitInfo(profitPercentage)
		}
		pm.PaperInfo.Volume += cashReceived
		pm.calcFees()
		averagePrice := cashReceived / amntFlt
		log.Println("Exited ", coin, ": ", amntFlt, "@", averagePrice)
		slippage := 100.0 * ((averagePrice / targetPrice) - 1.0)
		log.Println("Slippage: ", slippage)
		sendExit(pm.FrontendSocket, coin, portionToSell.String(), fmt.Sprintf("%f", averagePrice))
		return cashReceived
	} else {
		return 0.0
	}
}

func (pm *PortfolioManager) calcFees() {
	foundTier := false
	for amnt, fee := range coinbaseTakerFees {
		if amnt > pm.PaperInfo.Volume {
			pm.PaperInfo.TakerFee = fee
			foundTier = true
			break
		}
	}
	if !foundTier {
		pm.PaperInfo.TakerFee = 0.0004
	}

	return
}
