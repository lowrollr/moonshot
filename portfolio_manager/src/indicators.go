package main

import (
	"gopkg.in/karalabe/cookiejar.v1/collections/deque"
)

type RateOfChange struct {
	Values   *deque.Deque
	MaxLen   float64
	LeftVal  float64
	RightVal float64
}

func (roc *RateOfChange) Update(closePrice float64) {
	roc.RightVal = closePrice
	roc.Values.PushRight(closePrice)
	if roc.Values.Size() > roc.MaxLen {
		roc.Values.PopLeft()
	}
	roc.LeftVal = float64(roc.Values.Left().(float64))
}

func (roc *RateOfChange) GetVal() float64 {
	return (roc.RightVal - roc.LeftVal) / roc.LeftVal
}
