package main

import "math"

type Strategy struct {
	Data  map[int32]map[string]float32
	Coins []string
}

type Atlas struct {
	*Strategy
	LookingToEnter map[string]bool
	LimitUp        map[string]float32
	StopLoss       map[string]float32
}

type AtlasData struct {
	Close        float32
	RateOfChange float32
	SMA          float32
	Time         int64
}

func initStrategy(_coins *[]string) *Strategy {
	var strat Strategy
	strat.Data = make(map[int32]map[string]float32)
	strat.Coins = *_coins
	return &strat
}

func initAtlas(_coins *[]string) *Atlas {
	var atlas Atlas
	atlas.LookingToEnter = make(map[string]bool)
	atlas.LimitUp = make(map[string]float32)
	atlas.StopLoss = make(map[string]float32)
	atlas.Strategy = initStrategy(_coins)
	for _, coin := range atlas.Strategy.Coins {
		atlas.LookingToEnter[coin] = false
		atlas.LimitUp[coin] = 0.0
		atlas.StopLoss[coin] = 0.0
	}
	return &atlas
}

func (atlas *Atlas) Process(data *AtlasData, coinName string) {
	if atlas.StopLoss[coinName] > 0 {
		atlas.StopLoss[coinName] = maxFloat32(atlas.StopLoss[coinName], data.Close*0.995)
	}
	return
}

func (atlas *Atlas) CalcEnter(data *AtlasData, coinName string) bool {
	if atlas.LookingToEnter[coinName] && data.Close > atlas.LimitUp[coinName] {
		atlas.LookingToEnter[coinName] = false
		return true
	}
	atlas.LookingToEnter[coinName] = false

	//Make prediction call to the beverly hills here
	//so have to make prediction with all data inside here... features also have to be here?
	//when should features be computed? Not every time right?
	prediction := true

	if prediction && data.Close < data.SMA*0.97 {
		atlas.LimitUp[coinName] = data.Close * 1.005
		atlas.LookingToEnter[coinName] = true
	}
	return false
}

func (atlas *Atlas) CalcExit(data *AtlasData, coinName string) bool {
	amntAbove := maxFloat32(-0.015, data.RateOfChange/2)
	if data.Close > data.SMA*(1+amntAbove) {
		atlas.StopLoss[coinName] = maxFloat32(atlas.StopLoss[coinName], data.Close*0.995)
	}
	if data.Close < atlas.StopLoss[coinName] {
		atlas.StopLoss[coinName] = 0.0
		return true
	}
	return false
}

func maxFloat32(x, y float32) float32 {
	return float32(math.Max(float64(x), float64(y)))
}
