package main

import (
	"strconv"
	"time"

	coinbasepro "github.com/preichenberger/go-coinbasepro"
	log "github.com/sirupsen/logrus"
	"gopkg.in/karalabe/cookiejar.v1/collections/deque"
	// "sort"
	// "math"
)

type CoinInfo struct {
	LastClosePrice     float32
	InPosition         bool
	EnterValue         float32
	CashInvested       float32
	LastStartTime      int32
	RecentTradeResults *deque.Deque
	Allocation         float32
	AvgProfit          float32
	WinRate            float32
	AvgWin             float32
	AvgLoss            float32
}

type PortfolioManager struct {
	Strat             *interface{}
	ClientConnections map[string]*Client
	FrontendSocket    *ServerClient
	CoinDict          map[string]*CoinInfo
	Coins             *[]string
	FreeCash          float32
	PortfolioValue    float32
	CoinbaseClient    *coinbasepro.Client
}

type EnterSignal struct {
	Coin   string
	Profit float32
}

func initPM() *PortfolioManager {
	//starting cash commes from binance init
	time.Sleep(2)
	mapDomainConnection := StartClient()
	coins := mapDomainConnection[domainToUrl["main_data_consumer"]].GetCoins("main_data_consumer")
	client := coinbasepro.NewClient()
	accounts, err := client.GetAccounts()
	if err != nil {
		println(err.Error())
	}

	log.Println(marketOrder(client, "BTC", 20000.00, true))
	log.Println(marketOrder(client, "BTC", 15000.00, false))

	coinInfoDict := make(map[string]*CoinInfo)
	for _, coin := range *coins {
		coinInfoDict[coin] = &CoinInfo{
			LastClosePrice:     0.0,
			InPosition:         false,
			EnterValue:         0.0,
			CashInvested:       0.0,
			LastStartTime:      0,
			RecentTradeResults: deque.New(),
			Allocation:         0.0,
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
			cashAvailable, err := strconv.ParseFloat(a.Available, 32)
			if err == nil {
				pm.FreeCash = float32(cashAvailable)
			}
			portfolioValue, err := strconv.ParseFloat(a.Balance, 32)
			if err == nil {
				pm.PortfolioValue = float32(portfolioValue)
			}

			break
		}
	}

	mapDomainConnection[domainToUrl["beverly_hills"]].StartRemoteServer("beverly_hills")
	pm.ClientConnections = mapDomainConnection
	return pm
}

func (pm *PortfolioManager) StartTrading() {
	for {
		time.Sleep(time.Second)
	}
	//do any more init things that have to happen here
	//send start to the data consumer
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

func CalcKellyPercent(info *CoinInfo, maxlen int) float32 {
	// low_amnt := 0.01
	default_amnt := 0.05
	if info.RecentTradeResults.Size() == maxlen {
		// if info.avg_win && info.avg_loss {
		// 	kelly := info.win_rate - ((1 - info.win_rate) /(info.avg_win/math.Abs(info.avg_loss)))
		// 	if kelly > 0 {
		// 		return kelly
		// 	} else {
		// 		return float32(low_amnt)
		// 	}
		// }
	}
	return float32(default_amnt)
}

func (pm PortfolioManager) getPositions() []*CoinInfo {
	positions := []*CoinInfo{}
	// for i, coin := range *pm.coins {

	// }
	return positions
}

func enterPosition(coin string, cash_allocated float32) float32 {
	//enter the position in coin

	// return the amount of cash we actually allocated to the position, assuming it could be
	// slightly different than the amount of cash we intended to allocate
	return 0.0
}

func exitPosition(coin string) float32 {
	//exit the position in coin

	new_cash := 0.0

	// return the resultant cash we acquire from exiting the position
	return float32(new_cash)
}
