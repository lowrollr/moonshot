package main

import (
	"gopkg.in/karalabe/cookiejar.v1/collections/deque"
	"sort"
	"math"
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
	coinDict map[string] *CoinInfo
	coins *[]string
	strat *Strategy
	free_cash float32
	portfolio_value float32
}

type EnterSignal struct {
	coin string
	profit float32
}

func initPM(coins *[]string, strat *Strategy, starting_cash float32) *PortfolioManager {
	coinInfoDict := make(map[string]CoinInfo)
	for _, coin := range coins {
		coinInfoDict[coin] = &CoinInfo{
			last_close_price: 0.0,
			in_position:          false,
			enter_value:          0.0,
			cash_invested:        0.0,
			last_start_time:      0,
			recent_trade_results: deque.New(),
			allocation: 0.0,
			avg_profit: 0.0,
			win_rate: 0.0,
			avg_win: 0.0,
			avg_loss: 0.0
		}
	}
	pm := &PortfolioManager{coinInfo, coins, strat, starting_cash, starting_cash}
	return pm
}

func (pm PorfolioManager) PMAction(coin string, data *CandlestickData) {
	recent_trades_maxlen := 20
	strat := pm.strat
	info := pm.coinDict[coin]
	strat_data := strat.ProcessData(data)
	strat.Process(strat_data)
	enter_singals := []EnterSignal{}
	if info.in_position {
		if strat.CalcEnter(strat_data, coin){
			append(enter_singals, EnterSignal{coin, info.avg_profit})
		}

	}
	else{
		if strat.CalcExit(strat_data, coin){
			pm.cash += exitPosition(coin)
		}
	}
	
	sort.Slice(enter_singals, func(i, j int) bool {
		return enter_signals[i].avg_profit > enter_signals[j].avg_profit
	})
	for i, sig := range enter_signals {
		allocation := CalcKellyPercent(pm.coinDict[sig.coin], recent_trades_maxlen)
		// somewhere we need to update the portfolio value 
		cash_allocated := allocation * (pm.portfolio_value)
		if cash_allocated > pm.cash {
			cash -= enterPosition(coin, cash_allocated)

		}
		else {

		}
	}
	
	
	
}


func CalcKellyPercent(info *CoinInfo, maxlen int) float32 {
	low_amnt := 0.01
	default_amnt := 0.05
	if info.trades.Size() == maxlen {
		if info.avg_win && info.avg_loss {
			kelly := info.win_rate - ((1 - info.win_rate) /(info.avg_win/math.Abs(info.avg_loss)))
			if kelly > 0 {
				return kelly
			} 
			else {
				return low_amnt
			}
		}
	}

	return default_amnt
}

func (pm PortfolioManager) getPositions() []*CoinInfo {
	positions := []*CoinInfo
	for i, coin in pm.coins {
		
	}
	return positions
}

func enterPosition(coin string, cash_allocated float32) float32{
	//enter the position in coin

	// return the amount of cash we actually allocated to the position, assuming it could be 
	// slightly different than the amount of cash we intended to allocate
	return 
}

func exitPosition(coin string) float32{
	//exit the position in coin



	new_cash := 0.0

	// return the resultant cash we acquire from exiting the position
	return new_cash
}