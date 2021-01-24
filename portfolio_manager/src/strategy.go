package main

import "math"

type Strategy struct {
	data  map[int32]map[string]float32
	coins []string
}

type Atlas struct {
	*Strategy
	looking_to_enter map[string]bool
	limit_up         map[string]float32
	stop_loss        map[string]float32
}

type AtlasData struct {
	Close        float32
	RateOfChange float32
	SMA          float32
	Time         int64
}

func initStrategy(_coins *[]string) *Strategy {
	var strat Strategy
	strat.data = make(map[int32]map[string]float32)
	strat.coins = *_coins
	return &strat
}

func initAtlas(_coins *[]string) *Atlas {
	var atlas Atlas
	atlas.Strategy = initStrategy(_coins)
	for _, coin := range atlas.Strategy.coins {
		atlas.looking_to_enter[coin] = false
		atlas.limit_up[coin] = 0.0
		atlas.stop_loss[coin] = 0.0
	}
	return &atlas
}

//I know it's not a float but dunno how to do the data rn
func (atlas *Atlas) Process(data *AtlasData, coinName string) {
	if atlas.stop_loss[coinName] > 0 {
		atlas.stop_loss[coinName] = maxFloat32(atlas.stop_loss[coinName], data.Close*0.995)
	}
	return
}

func (atlas *Atlas) CalcEnter(data *AtlasData, coinName string) bool {
	if atlas.looking_to_enter[coinName] && data.Close > atlas.limit_up[coinName] {
		atlas.looking_to_enter[coinName] = false
		return true
	}
	atlas.looking_to_enter[coinName] = false

	//Make prediction call to the beverly hills here
	//so have to make prediction with all data inside here... features also have to be here?
	//when should features be computed? Not every time right?
	prediction := true

	if prediction && data.Close < data.SMA*0.97 {
		atlas.limit_up[coinName] = data.Close * 1.005
		atlas.looking_to_enter[coinName] = true
	}
	return false
}

func (atlas *Atlas) CalcExit(data *AtlasData, coinName string) bool {
	amntAbove := maxFloat32(-0.015, data.RateOfChange/2)
	if data.Close > data.SMA*(1+amntAbove) {
		atlas.stop_loss[coinName] = maxFloat32(atlas.stop_loss[coinName], data.Close*0.995)
	}
	if data.Close < atlas.stop_loss[coinName] {
		atlas.stop_loss[coinName] = 0.0
		return true
	}
	return false
}

func maxFloat32(x, y float32) float32 {
	return float32(math.Max(float64(x), float64(y)))
}
