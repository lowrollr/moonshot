package main

type Strategy struct {
	data  map[int32]map[string]float32
	coins []string
}

func initStrategy(_coins *[]string) *Strategy {
	var strat Strategy
	strat.data = make(map[int32]map[string]float32)
	strat.coins = *_coins
	return &strat
}

type Atlas struct {
	*Strategy
	looking_to_enter map[string]bool
	limit_up         map[string]float32
	stop_loss        map[string]float32
}
