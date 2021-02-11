package main

import (
	"net"
	"time"

	log "github.com/sirupsen/logrus"
	"gopkg.in/karalabe/cookiejar.v1/collections/deque"
	// "sort"
	// "math"
)

type CoinInfo struct {
	last_close_price     float32
	in_position          bool
	enter_value          float32
	cash_invested        float32
	last_start_time      int32
	recent_trade_results *deque.Deque
	allocation           float32
	avg_profit           float32
	win_rate             float32
	avg_win              float32
	avg_loss             float32
}

type PortfolioManager struct {
	strat             *interface{}
	clientConnections map[string]*net.Conn
	FrontendSocket    *ServerClient
	coinDict          map[string]*CoinInfo
	coins             *[]string
	free_cash         float32
	portfolio_value   float32
}

type EnterSignal struct {
	coin   string
	profit float32
}

func initPM(starting_cash float32) *PortfolioManager {
	//starting cash commes from binance init
	mapDomainConnection := startClient()
	coins := getCoins(mapDomainConnection[domainToUrl["main_data_consumer"]])

	coinInfoDict := make(map[string]*CoinInfo)
	for _, coin := range *coins {
		coinInfoDict[coin] = &CoinInfo{
			last_close_price:     0.0,
			in_position:          false,
			enter_value:          0.0,
			cash_invested:        0.0,
			last_start_time:      0,
			recent_trade_results: deque.New(),
			allocation:           0.0,
			avg_profit:           0.0,
			win_rate:             0.0,
			avg_win:              0.0,
			avg_loss:             0.0,
		}
	}
	pm := &PortfolioManager{clientConnections: mapDomainConnection,
		coinDict:        coinInfoDict,
		coins:           coins,
		free_cash:       starting_cash,
		portfolio_value: starting_cash,
	}

	StartRemoteServer(mapDomainConnection[domainToUrl["beverly_hills"]], "beverly_hills")
	pm.clientConnections = mapDomainConnection
	return pm
}

func (pm *PortfolioManager) StartTrading() {
	log.Println("hi")
	for {
		time.Sleep(time.Second)
	}
	//do any more init things that have to happen here

	//send start to the data consumer
	StartRemoteServer(pm.clientConnections[domainToUrl["main_data_consumer"]], "main_data_consumer")

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
	if info.recent_trade_results.Size() == maxlen {
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
