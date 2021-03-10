/*
FILE: pm.go
AUTHORS:
	-> Jacob Marshall <marshingjay@gmail.com>
	-> Ross Copeland <rhcopeland101@gmail.com>
WHAT:
	-> Contains implementations of a generic strategy as well as specific strategies
*/

package main

import (
	"math"

	"gopkg.in/karalabe/cookiejar.v2/collections/deque"
)

// Base strategy
type Strategy struct {
	Coins []string // list of coins that the strategy will be trading upon
}

// 'Atlas' strategy
type Atlas struct {
	Strategy          *Strategy                // base strategy object
	StopLoss          map[string]float64       // map coin -> stop loss
	RateOfChangeShort map[string]*RateOfChange // map coin -> RateOfChange indicator
	SMAGoal           map[string]*SMA          // map coin -> SMA indicator SMAGoal
	SMAShort          map[string]*SMA          // map coin -> SMA indicator SMAShort
}

/*
	ARGS:
		-> coins (*[]string): list of coins that the strategy will be trading
    RETURN:
        -> strat (*Strategy): an initialized Strategy object
    WHAT:
		-> initializes a new strategy object with the passed coins
*/
func initStrategy(coins *[]string) *Strategy {
	var strat Strategy
	strat.Coins = *coins
	return &strat
}

/*
	ARGS:
		-> coins (*[]string): list of coins that the Atlas strategy will be trading
    RETURN:
        -> atlas (*Atlas): an initialized Atlas object
    WHAT:
		-> initializes a new Atlas strategy object with the given coins
		-> each field maps coin -> some variable
		-> since each coin is passed into this same object when trading, we need to keep track of variables on a per-coin basis
*/
func initAtlas(coins *[]string) *Atlas {
	// initialize a new Atlas object
	var atlas Atlas

	// create the stop loss map
	atlas.StopLoss = make(map[string]float64)

	// create the map for the RateOfChange (RateOfChangeShort) indicator
	atlas.RateOfChangeShort = make(map[string]*RateOfChange)

	// create the map for the SMA (SMAGoal) indicator
	atlas.SMAGoal = make(map[string]*SMA)

	// create the map for the SMA (SMAShort) indicator
	atlas.SMAShort = make(map[string]*SMA)

	// initialize the underlying base strategy object
	atlas.Strategy = initStrategy(coins)

	// initialize map values for each coin
	for _, coin := range atlas.Strategy.Coins {
		atlas.StopLoss[coin] = 0.0
		// map to new SMA object with appropriate period
		atlas.SMAGoal[coin] = &SMA{
			Values: deque.New(),
			MaxLen: 150,
			CurSum: 0,
		}
		// map to new SMA object with appropriate period
		atlas.SMAShort[coin] = &SMA{
			Values: deque.New(),
			MaxLen: 30,
			CurSum: 0,
		}
		// map to new RateOfChange object with appropriate period
		atlas.RateOfChangeShort[coin] = &RateOfChange{
			Values:   deque.New(),
			MaxLen:   45,
			LeftVal:  1,
			RightVal: 1,
		}
	}

	// return the initialized Atlas object
	return &atlas
}

/*
	RECEIVER:
		-> atlas (*Atlas): Atlas object
	ARGS:
		-> data (CandlestickData): CandlestickData object holding most recent candlestick for the given coin
		-> coinName (string): the coin that the candle belongs to
    RETURN:
        -> N/A
    WHAT:
		-> Process is called every tick
		-> computes things that need to be update every tick (like indicators)
		-> also updates the trailing stop loss
*/
func (atlas *Atlas) Process(data CandlestickData, coinName string) {
	// compute indicators that require base candlestick values (like Close) as input
	atlas.SMAShort[coinName].Update(data.Close)
	atlas.SMAGoal[coinName].Update(data.Close)

	// compute indicators that require other indicators as input
	atlas.RateOfChangeShort[coinName].Update(atlas.SMAShort[coinName].GetVal())

	// update the trailing stop loss
	if atlas.StopLoss[coinName] > 0 {
		atlas.StopLoss[coinName] = math.Max(atlas.StopLoss[coinName], data.Close*0.995)
	}
	return
}

/*
	RECEIVER:
		-> atlas (*Atlas): Atlas object
	ARGS:
		-> data (CandlestickData): CandlestickData object holding most recent candlestick for the given coin
		-> coinName (string): the coin that the candle belongs to
		-> bhconn (*Client): websocket connection to beverly hills, used to request model prediction
    RETURN:
        -> (bool): true if it is determined a position should be entered, false if not
    WHAT:
		-> Calculates whether or not a position in the coin should be entered
		-> if other conditions are met, requests a prediction from Beverly Hills (where the models live)
*/
func (atlas *Atlas) CalcEnter(data CandlestickData, coinName string, bhconn *Client) bool {

	//  if the Close price is 3% below the given SMA, check for a prediction
	if data.Close < atlas.SMAGoal[coinName].GetVal()*0.97 {

		// get the prediction from Beverly Hills
		prediction := GetPrediction(bhconn, coinName, data.StartTime)

		// if the prediction comes back positive, return true
		if prediction {
			return true
		}
	}

	// if the condition is not met or there is no signal from the model, return false
	return false
}

/*
	RECEIVER:
		-> atlas (*Atlas): Atlas object
	ARGS:
		-> data (CandlestickData): CandlestickData object holding most recent candlestick for the given coin
		-> coinName (string): the coin that the candle belongs to
    RETURN:
        -> (bool): true if it is determined the position should be exited, false if not
    WHAT:
		-> Calculates whether or not the position in the coin should be exited
*/
func (atlas *Atlas) CalcExit(data CandlestickData, coinName string) bool {

	// calculate how far above the SMA to increase the threshold to given the current rate of change (from RateOfChangeShort)
	amntAbove := math.Max(-0.01, atlas.RateOfChangeShort[coinName].GetVal())

	// if the Close price is <amntAbove>% above (below if negative) the given SMA, set the stop loss to be a tight value (0.5%) below the Close
	if data.Close > atlas.SMAGoal[coinName].GetVal()*(1+amntAbove) {
		atlas.StopLoss[coinName] = math.Max(atlas.StopLoss[coinName], data.Close*0.995)
	}

	// if the close price is below the stop loss, reset the stop loss and return true
	if data.Close < atlas.StopLoss[coinName] {
		atlas.StopLoss[coinName] = 0.0
		return true
	}

	// otherwise, return false
	return false
}
