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

func (roc *RateOfChange) Update(newVal float64) {
	roc.RightVal = newVal
	roc.Values.PushRight(newVal)
	if roc.Values.Size() > roc.MaxLen {
		roc.Values.PopLeft()
	}
	roc.LeftVal = float64(roc.Values.Left().(float64))
}

func (roc *RateOfChange) GetVal() float64 {
	return (roc.RightVal - roc.LeftVal) / roc.LeftVal
}

type SMA struct {
	Values *deque.Deque
	MaxLen float64
	CurSum float64
}

func (sma *SMA) Update(newVal float64) {
	sma.Values.PushRight(newVal)
	sma.CurSum += newVal
	if sma.Values.Size() > sma.MaxLen {
		removedVal := float64(sma.Values.PopLeft().(float64))
		sma.CurSum -= newVal
	}
}

func (sma *SMA) GetVal() float64 {
	return sma.CurSum / sma.MaxLen
}
