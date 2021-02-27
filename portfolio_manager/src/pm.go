package main

import (
	"math"
	"sort"
	"strconv"
	"strings"
	"time"

	coinbasepro "github.com/preichenberger/go-coinbasepro"
	decimal "github.com/shopspring/decimal"
	log "github.com/sirupsen/logrus"
	"gopkg.in/karalabe/cookiejar.v1/collections/deque"
	// "sort"
	// "math"
)

type ProfitQueue struct {
	Results *deque.Deque
	SumOvr  float64
	SumPos  float64
	SumNeg  float64
	NumPos  int
	NumNeg  int
	NumOvr  int
}

type CoinInfo struct {
	InPosition       bool
	EnterPrice       decimal.Decimal
	EnterPriceFl     float64
	AmntOwned        decimal.Decimal
	CashInvested     float64
	ProfitHistory    *ProfitQueue
	AvgProfit        float64
	WinRate          float64
	AvgWin           float64
	AvgLoss          float64
	IntermediateCash float64
	CoinOrderBook    *OrderBook
}

type PortfolioManager struct {
	MakerFee          float64
	TakerFee          float64
	Strat             *Atlas
	ClientConnections map[string]*Client
	FrontendSocket    *ServerClient
	CoinDict          map[string]*CoinInfo
	Coins             *[]string
	FreeCash          float64
	PortfolioValue    float64
	CoinbaseClient    *coinbasepro.Client
	TradesToCalibrate int
	CandleDict        map[string]CandlestickData
}

type EnterSignal struct {
	Coin   string
	Profit float64
}

func initPM() *PortfolioManager {
	mapDomainConnection := StartClient()
	coins := mapDomainConnection[domainToUrl["main_data_consumer"]].GetCoins("main_data_consumer")
	strategy := initAtlas(coins)

	client := coinbasepro.NewClient()
	accounts, err := client.GetAccounts()
	if err != nil {
		println(err.Error())
	}
	candleDict := make(map[string]CandlestickData)
	coinInfoDict := make(map[string]*CoinInfo)
	for _, coin := range *coins {
		coinInfoDict[coin] = &CoinInfo{
			InPosition:   false,
			EnterPrice:   decimal.NewFromFloat(0.0),
			EnterPriceFl: -1.0,
			AmntOwned:    decimal.NewFromFloat(0.0),
			ProfitHistory: &ProfitQueue{
				Results: deque.New(),
				SumNeg:  0,
				SumPos:  0,
				SumOvr:  0,
				NumOvr:  0,
				NumPos:  0,
				NumNeg:  0,
			},
			AvgProfit:        0.0,
			WinRate:          0.0,
			AvgWin:           0.0,
			AvgLoss:          0.0,
			IntermediateCash: 0.0,
			CoinOrderBook:    nil,
		}
	}
	pm := &PortfolioManager{
		ClientConnections: mapDomainConnection,
		CoinDict:          coinInfoDict,
		Coins:             coins,
		FreeCash:          0.0,
		PortfolioValue:    0.0,
		CoinbaseClient:    client,
		TradesToCalibrate: 20,
		Strat:             strategy,
		MakerFee:          0.5,
		TakerFee:          0.5,
		CandleDict:        candleDict,
	}
	for _, a := range accounts {
		// is account USD
		currency := a.Currency
		if currency == "USD" {
			cashAvailable, err := strconv.ParseFloat(a.Available, 64)
			if err == nil {
				pm.FreeCash = cashAvailable
			}
			portfolioValue, err := strconv.ParseFloat(a.Balance, 64)
			if err == nil {
				pm.PortfolioValue = portfolioValue
			}

			break
		}
	}
	fees, err := client.GetFees()
	if err != nil {
		log.Println("Error fetching account fees!")
	} else {
		pm.MakerFee, _ = strconv.ParseFloat(fees.MakerFeeRate, 64)
		pm.TakerFee, _ = strconv.ParseFloat(fees.TakerFeeRate, 64)
	}
	// log.Println(pm.CoinDict["BTC"])
	// pm.enterPosition("BTC", 20000)
	// log.Println(pm.CoinDict["BTC"])
	// log.Println(pm.CoinDict["BTC"].AmntOwned)

	// pm.exitPosition("BTC", pm.CoinDict["BTC"].AmntOwned)
	// log.Println(pm.CoinDict["BTC"])

	mapDomainConnection[domainToUrl["beverly_hills"]].StartRemoteServer("beverly_hills")
	mapDomainConnection[domainToUrl["main_data_consumer"]].StartRemoteServer("main_data_consumer")

	pm.ClientConnections = mapDomainConnection
	return pm
}

func (pm *PortfolioManager) StartTrading() {
	time.Sleep(1 * time.Second)
	pm.PortfolioValue = pm.CalcPortfolioValue()

	for {

		newCandleData := *pm.ClientConnections[domainToUrl["main_data_consumer"]].ReceiveCandleData()
		if len(newCandleData) > 0 {
			pm.CandleDict = newCandleData
			pm.PMProcess()
		}
		pm.PortfolioValue = pm.CalcPortfolioValue()
	}

}

func (pm *PortfolioManager) PMProcess() {

	// check for buy/sell signals from strategy
	enter_coins := []string{}
	for _, coin := range *pm.Coins {
		candle := pm.CandleDict[coin]
		pm.Strat.Process(candle, coin)
		if pm.CoinDict[coin].InPosition {
			if pm.Strat.CalcExit(candle, coin) {
				pm.PortfolioValue += pm.exitPosition(coin, pm.CoinDict[coin].AmntOwned)
			}
		} else {
			if pm.Strat.CalcEnter(candle, coin, pm.ClientConnections[domainToUrl["beverly_hills"]]) {
				enter_coins = append(enter_coins, coin)
			}
		}
	}
	if len(enter_coins) > 0 {
		pm.SortByProfit(&enter_coins)
	}
	for _, coin := range enter_coins {
		allocation := CalcKellyPercent(pm.CoinDict[coin], pm.TradesToCalibrate)
		cashToAllocate := pm.PortfolioValue * allocation
		if cashToAllocate < pm.FreeCash {
			cashUsed := pm.enterPosition(coin, cashToAllocate)
			pm.FreeCash -= cashUsed
		} else {
			// all coins in positions sorted by EV
			pmCoins := pm.Coins
			evMap := pm.SortByEV(pm.GetCoinsInPosition(*pmCoins))
			for _, coinIn := range *pmCoins {
				if !(ExistsInSlice(coinIn, &enter_coins)) {

					if cashToAllocate <= pm.FreeCash || ((*evMap)[coinIn] > pm.CoinDict[coinIn].AvgProfit && pm.CoinDict[coinIn].ProfitHistory.Results.Size() > 0) {
						break
					}

					amntOwnedStr := pm.CoinDict[coinIn].AmntOwned.String()
					amntOwnedFlt, _ := strconv.ParseFloat(amntOwnedStr, 64)
					curCashValue := pm.CandleDict[coinIn].Close * amntOwnedFlt
					cashNeeded := curCashValue - pm.FreeCash

					if pm.FreeCash == 0 || cashNeeded >= 0.5*curCashValue {
						cashReceived := pm.exitPosition(coinIn, pm.CoinDict[coinIn].AmntOwned)
						pm.FreeCash += cashReceived
					} else {
						amntToSell := (cashNeeded / curCashValue) * amntOwnedFlt
						// partially exit position
						cashReceived := pm.exitPosition(coinIn, decimal.NewFromFloat(amntToSell))
						pm.FreeCash = cashReceived
					}
				}
				if pm.FreeCash > 0 {
					amntToAllocate := math.Min(pm.FreeCash, cashToAllocate)
					cashUsed := pm.enterPosition(coin, amntToAllocate)
					pm.FreeCash -= cashUsed
				}
			}
		}
	}
}

func ExistsInSlice(coin string, slice *[]string) bool {
	for _, item := range *slice {
		if item == coin {
			return true
		}
	}
	return false
}

func (pm *PortfolioManager) GetCoinsInPosition(coins []string) *[]string {
	coinsInPosition := []string{}
	for _, coin := range coins {
		if pm.CoinDict[coin].InPosition {
			coinsInPosition = append(coinsInPosition, coin)
		}
	}
	return &coinsInPosition
}

func (pm *PortfolioManager) CalcPortfolioValue() float64 {
	total_value := pm.FreeCash
	for _, coin := range *pm.Coins {
		if pm.CoinDict[coin].InPosition {
			amntOwnedFlt, _ := strconv.ParseFloat(pm.CoinDict[coin].AmntOwned.String(), 64)
			total_value += amntOwnedFlt * pm.CandleDict[coin].Close
		}
	}
	return total_value
}

func (pm *PortfolioManager) SortByProfit(coins *[]string) {
	sort.Slice(*coins, func(i, j int) bool {
		return pm.CoinDict[(*coins)[i]].AvgProfit > pm.CoinDict[(*coins)[j]].AvgProfit
	})
}

func (pm *PortfolioManager) SortByEV(coins *[]string) *map[string]float64 {
	evMap := make(map[string]float64)
	for _, coin := range *coins {

		enterPrice := pm.CoinDict[coin].EnterPriceFl
		expectedValue := pm.CoinDict[coin].AvgProfit - ((pm.CandleDict[coin].Close - enterPrice) / enterPrice)
		evMap[coin] = expectedValue

	}
	sort.Slice(*coins, func(i, j int) bool {
		return evMap[(*coins)[i]] > evMap[(*coins)[j]]
	})

	return &evMap
}

func CalcKellyPercent(info *CoinInfo, maxlen int) float64 {
	low_amnt := 0.01
	default_amnt := 0.05
	if info.ProfitHistory.Results.Size() == maxlen {
		if info.AvgWin != 0.0 && info.AvgLoss != 0.0 {
			kelly := info.WinRate - ((1 - info.WinRate) / (info.AvgWin / math.Abs(info.AvgLoss)))
			if kelly > 0 {
				return kelly
			} else {
				return low_amnt
			}
		}
	}
	return default_amnt
}

func (pm *PortfolioManager) enterPosition(coin string, cashAllocated float64) float64 {
	filledOrder := marketOrder(pm.CoinbaseClient, coin, decimal.NewFromFloat(cashAllocated), true)
	log.Println(filledOrder)
	info := pm.CoinDict[coin]
	if filledOrder.Settled {
		info.InPosition = true
		info.CashInvested = cashAllocated
		execValue, _ := decimal.NewFromString(filledOrder.ExecutedValue)
		fillSize, _ := decimal.NewFromString(filledOrder.FilledSize)
		info.EnterPrice = execValue.Div(fillSize)
		enterPriceFl, _ := strconv.ParseFloat(info.EnterPrice.String(), 64)
		info.EnterPriceFl = enterPriceFl
		info.AmntOwned = fillSize
		sendEnter(pm.FrontendSocket, coin, filledOrder.FilledSize, info.EnterPrice.String())
		return cashAllocated
	} else {
		return 0.0
	}
}

func (pm *PortfolioManager) exitPosition(coin string, portionToSell decimal.Decimal) float64 {
	filledOrder := marketOrder(pm.CoinbaseClient, coin, portionToSell, false)
	log.Println(filledOrder)
	info := pm.CoinDict[coin]
	if filledOrder.Settled {

		execValue, _ := decimal.NewFromString(filledOrder.ExecutedValue)
		fees, _ := decimal.NewFromString(filledOrder.FillFees)
		newCash, _ := strconv.ParseFloat(execValue.Sub(fees).String(), 64)

		if portionToSell != info.AmntOwned {
			info.IntermediateCash += newCash
		} else {
			info.InPosition = false

			profitPercentage := ((newCash + info.IntermediateCash) / info.CashInvested) - 1.0
			info.IntermediateCash = 0.0

			info.updateProfitInfo(profitPercentage)
		}

		sendExit(pm.FrontendSocket, coin, portionToSell.String(), filledOrder.ExecutedValue)
		return newCash
	} else {
		return 0.0
	}
}

func (info *CoinInfo) updateProfitInfo(profitPercentage float64) {

	profitQueue := info.ProfitHistory

	profitQueue.Results.PushRight(profitPercentage)
	profitQueue.SumOvr += profitPercentage
	profitQueue.NumOvr += 1
	if profitPercentage > 0 {
		profitQueue.SumPos += profitPercentage
		profitQueue.NumPos += 1
	} else if profitPercentage < 0 {
		profitQueue.SumNeg += profitPercentage
		profitQueue.NumNeg += 1
	}
	if profitQueue.Results.Size() > 20 {
		oldVal := float64(profitQueue.Results.PopLeft().(float64))
		profitQueue.SumOvr -= oldVal
		profitQueue.NumOvr -= 1
		if oldVal > 0 {
			profitQueue.SumPos -= oldVal
			profitQueue.NumPos -= 1
		} else {
			profitQueue.SumNeg -= oldVal
			profitQueue.NumNeg -= 1
		}
	}

	info.AvgLoss = profitQueue.SumNeg / float64(profitQueue.NumNeg)
	info.AvgWin = profitQueue.SumPos / float64(profitQueue.NumPos)
	info.AvgProfit = profitQueue.SumOvr / float64(profitQueue.NumOvr)
	info.WinRate = float64(profitQueue.NumPos) / float64(profitQueue.NumOvr)
}

func (pm *PortfolioManager) ReadOrderBook(initialized chan bool) {
	fullyInitialized := false
	coinsInitalized := 0

	for {
		log.Println("Starting level2 order book socket initialization")
		conn, err := ConnectToCoinbaseOrderBookSocket(pm.Coins)
		if err != nil {
			log.Panic("Was not able to open websocket with error: " + err.Error())
		}
		// get initial
		for {
			message := CoinBaseMessage{}
			if err := conn.ReadJSON(&message); err != nil {
				log.Warn("Was not able to retrieve message with error: " + err.Error())
				conn.Close()
				log.Warn("Attempting to restart connection...")
				break
			}
			if message.Type == "snapshot" {
				coin := strings.Split(message.ProductID, "-")[0]
				if pm.CoinDict[coin].CoinOrderBook == nil {
					pm.CoinDict[coin].CoinOrderBook = InitOrderBook(&message.Bids, &message.Asks)
					coinsInitalized++
					if coinsInitalized == len(*pm.Coins) && !fullyInitialized {
						fullyInitialized = true
						initialized <- true
					}
				}
			} else if message.Type == "l2update" {
				coin := strings.Split(message.ProductID, "-")[0]
				for _, change := range message.Changes {
					if change[0] == "buy" {
						pm.CoinDict[coin].CoinOrderBook.Bids.Update(change[1], change[2])
					} else {
						pm.CoinDict[coin].CoinOrderBook.Asks.Update(change[1], change[2])
					}
				}
			} else if message.Type != "subscriptions" {
				log.Warn("Got wrong message type: " + message.Type)
				conn.Close()
				log.Warn("Attempting to restart connection...")
				break
			}
		}

	}
}
