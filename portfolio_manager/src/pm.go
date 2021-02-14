package main

import (
	"math"
	"net"
	"strconv"
	"time"

	coinbasepro "github.com/preichenberger/go-coinbasepro"
	decimal "github.com/shopspring/decimal"
	log "github.com/sirupsen/logrus"
	"gopkg.in/karalabe/cookiejar.v1/collections/deque"
	// "sort"
	// "math"
)

type CoinInfo struct {
	LastClosePrice     float64
	InPosition         bool
	EnterPrice         decimal.Decimal
	AmntOwned          decimal.Decimal
	CashInvested       float64
	RecentTradeResults *deque.Deque
	AvgProfit          float64
	WinRate            float64
	AvgWin             float64
	AvgLoss            float64
}

type PortfolioManager struct {
	Strat             *interface{}
	ClientConnections map[string]*net.Conn
	FrontendSocket    *ServerClient
	CoinDict          map[string]*CoinInfo
	Coins             *[]string
	FreeCash          float64
	PortfolioValue    float64
	CoinbaseClient    *coinbasepro.Client
}

type EnterSignal struct {
	Coin   string
	Profit float64
}

func initPM() *PortfolioManager {
	//starting cash commes from binance init
	mapDomainConnection := startClient()
	coins := getCoins(mapDomainConnection[domainToUrl["main_data_consumer"]])
	client := coinbasepro.NewClient()
	accounts, err := client.GetAccounts()
	if err != nil {
		println(err.Error())
	}

	coinInfoDict := make(map[string]*CoinInfo)
	for _, coin := range *coins {
		coinInfoDict[coin] = &CoinInfo{
			LastClosePrice:     0.0,
			InPosition:         false,
			EnterPrice:         decimal.NewFromFloat(0.0),
			AmntOwned:          decimal.NewFromFloat(0.0),
			RecentTradeResults: deque.New(),
			AvgProfit:          0.0,
			WinRate:            0.0,
			AvgWin:             0.0,
			AvgLoss:            0.0,
		}
	}
	pm := &PortfolioManager{ClientConnections: mapDomainConnection,
		CoinDict:       coinInfoDict,
		Coins:          coins,
		FreeCash:       0.0,
		PortfolioValue: 0.0,
		CoinbaseClient: client,
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
	log.Println(pm.CoinDict["BTC"])
	pm.enterPosition("BTC", 20000)
	log.Println(pm.CoinDict["BTC"])
	log.Println(pm.CoinDict["BTC"].AmntOwned)

	pm.exitPosition("BTC", pm.CoinDict["BTC"].AmntOwned)
	log.Println(pm.CoinDict["BTC"])

	// }

	StartRemoteServer(mapDomainConnection[domainToUrl["beverly_hills"]], "beverly_hills")
	pm.ClientConnections = mapDomainConnection
	return pm
}

func (pm *PortfolioManager) StartTrading() {
	log.Println("hi")
	for {
		time.Sleep(time.Second)
	}
	//do any more init things that have to happen here

	//send start to the data consumer
	StartRemoteServer(pm.ClientConnections[domainToUrl["main_data_consumer"]], "main_data_consumer")

}

func (pm *PortfolioManager) SetStrategy(strat interface{}) {
	//test if strat has the methods we need.
	// -> calcentry etc.
}

// func (pm *PortfolioManager) PMAction(coin string, data *CandlestickData) {
// 	recent_trades_maxlen := 20
// 	strat := pm.strat
// 	info := pm.coinDict[coin]
// 	strat_data := strat.ProcessData(data)
// 	strat.Process(strat_data)
// 	enter_singals := []EnterSignal{}
// 	if info.in_position {
// 		if strat.CalcEnter(strat_data, coin){
// 			append(enter_signals, EnterSignal{coin, info.avg_profit})
// 		}

// 	} else {
// 		if strat.CalcExit(strat_data, coin){
// 			pm.cash += exitPosition(coin)
// 		}
// 	}

// 	sort.Slice(enter_signals, func(i, j int) bool {
// 		return enter_signals[i].avg_profit > enter_signals[j].avg_profit
// 	})
// 	for i, sig := range enter_signals {
// 		allocation := CalcKellyPercent(pm.coinDict[sig.coin], recent_trades_maxlen)
// 		// somewhere we need to update the portfolio value
// 		cash_allocated := allocation * (pm.portfolio_value)
// 		if cash_allocated > pm.cash {
// 			cash -= enterPosition(coin, cash_allocated)

// 		} else {

// 		}
// 	}

// }

func CalcKellyPercent(info *CoinInfo, maxlen int) float64 {
	low_amnt := 0.01
	default_amnt := 0.05
	if info.RecentTradeResults.Size() == maxlen {
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

func (pm PortfolioManager) getPositions() []*CoinInfo {
	positions := []*CoinInfo{}
	// for i, coin := range *pm.coins {

	// }
	return positions
}

func (pm *PortfolioManager) enterPosition(coin string, cashAllocated float64) float64 {
	filledOrder := marketOrder(pm.CoinbaseClient, coin, decimal.NewFromFloat(cashAllocated), true)
	log.Println(filledOrder)
	info := pm.CoinDict[coin]
	if filledOrder.Settled {
		info.InPosition = true
		info.CashInvested = cashAllocated
		expValue, _ := decimal.NewFromString(filledOrder.ExecutedValue)
		fillSize, _ := decimal.NewFromString(filledOrder.FilledSize)
		info.EnterPrice = expValue.Div(fillSize)
		info.AmntOwned = fillSize
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
		info.InPosition = false
		expValue, _ := decimal.NewFromString(filledOrder.ExecutedValue)
		fees, _ := decimal.NewFromString(filledOrder.FillFees)
		newCash, _ := strconv.ParseFloat(expValue.Sub(fees).String(), 64)
		profitPercentage := 1.0 - (newCash / info.CashInvested)
		//calculate profit
		info.RecentTradeResults.PushRight(profitPercentage)
		if info.RecentTradeResults.Size() > 20 {
			info.RecentTradeResults.PopLeft()
		}
		// calculate profit and append trade to recentTradeResults
		return newCash
	} else {
		return 0.0
	}
}
