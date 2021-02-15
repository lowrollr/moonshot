package main

import (
	"math"

	"gopkg.in/karalabe/cookiejar.v1/collections/deque"
)

type Strategy struct {
	Coins []string
}

type Atlas struct {
	Strategy          *Strategy
	StopLoss          map[string]float64
	RateOfChangeShort map[string]*RateOfChange
	SMAGoal           map[string]*SMA
	SMAShort          map[string]*SMA
}

func initStrategy(_coins *[]string) *Strategy {
	var strat Strategy
	strat.Coins = *_coins
	return &strat
}

func initAtlas(_coins *[]string) *Atlas {
	var atlas Atlas
	atlas.StopLoss = make(map[string]float64)
	atlas.RateOfChangeShort = make(map[string]*RateOfChange)
	atlas.SMAGoal = make(map[string]*SMA)
	atlas.SMAShort = make(map[string]*SMA)
	atlas.Strategy = initStrategy(_coins)
	for _, coin := range atlas.Strategy.Coins {
		atlas.StopLoss[coin] = 0.0
		atlas.SMAGoal[coin] = &SMA{
			Values: deque.New(),
			MaxLen: 150,
			CurSum: 0,
		}
		atlas.SMAShort[coin] = &SMA{
			Values: deque.New(),
			MaxLen: 30,
			CurSum: 0,
		}
		atlas.RateOfChangeShort[coin] = &RateOfChange{
			Values:   deque.New(),
			MaxLen:   45,
			LeftVal:  1,
			RightVal: 1,
		}
	}
	return &atlas
}

func (atlas *Atlas) Process(data *CandlestickData, coinName string) {

	atlas.SMAShort[coinName].Update(data.Close)
	atlas.SMAGoal[coinName].Update(data.Close)
	atlas.RateOfChangeShort[coinName].Update(atlas.SMAShort[coinName].GetVal())
	if atlas.StopLoss[coinName] > 0 {
		atlas.StopLoss[coinName] = math.Max(atlas.StopLoss[coinName], data.Close*0.995)
	}
	return
}

func (atlas *Atlas) CalcEnter(data *CandlestickData, coinName string) bool {

	prediction := true

	if prediction && data.Close < atlas.SMAGoal[coinName].GetVal()*0.97 {
		return true
	}
	return false
}

func (atlas *Atlas) CalcExit(data *CandlestickData, coinName string) bool {
	amntAbove := math.Max(-0.01, atlas.RateOfChangeShort[coinName].GetVal())
	if data.Close > atlas.SMAGoal[coinName].GetVal()*(1+amntAbove) {
		atlas.StopLoss[coinName] = math.Max(atlas.StopLoss[coinName], data.Close*0.995)
	}
	if data.Close < atlas.StopLoss[coinName] {
		atlas.StopLoss[coinName] = 0.0
		return true
	}
	return false
}
