package main

import "gopkg.in/karalabe/cookiejar.v1/collections/deque"

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



func runPM(strat *Strategy) map[string]CoinInfo {
	coinInfoDict := make(map[string]CoinInfo)
	for _, coin := range coins {
		coinInfoDict[coin] = CoinInfo{
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
	for {
		for _, coin := range coins {
			//get data for coin that strategy needs to execute (i.e. algo indicators in backtesting)
			enter_singals := []string{}
			// call process for strategy
			strat.Process(data, coin)
			if coinInfoDict[coin].in_position{
				if strat.CalcEnter(data, coin){
					append(enter_singals, coin)
				}
				else if strat.CalcExit(data, coin){

				}
			}
		}
	}
}

func enterPosition(info *CoinInfo){
	
}