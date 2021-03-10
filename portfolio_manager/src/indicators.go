/*
FILE: indicators.go
AUTHORS:
	-> Jacob Marshall <marshingjay@gmail.com>
WHAT:
	-> This file contains indicator structs used within strategies, as well as functions that implement updating and calculating these indicators
*/

package main

import (
	"math"

	"gopkg.in/karalabe/cookiejar.v2/collections/deque"
)

// holds the 'rate of change' indicator
// rate of change = (new value - old value) / old value
type RateOfChange struct {
	Values   *deque.Deque // deque of values (size equal to period)
	MaxLen   int          // max length of queue (also equal to period)
	LeftVal  float64      // store leftmost value in queue for fast computation
	RightVal float64      // store rightmost value in queue for fast computation
}

/*
	RECEIVER:
		-> roc (*RateOfChange): rateOfChange object to update
	ARGS:
		-> newVal (float64): new value to add to the indicator's data queue
    RETURN:
        -> N/A
    WHAT:
		-> puts the new value into the data queue and updates LeftVal/RightVal
*/
func (roc *RateOfChange) Update(newVal float64) {
	// push the newValue onto the queue and update RightVal
	roc.RightVal = newVal
	roc.Values.PushRight(newVal)

	// if the queue is overfull, pop the leftmost element
	if roc.Values.Size() > roc.MaxLen {
		roc.Values.PopLeft()
	}
	// update LeftVal
	roc.LeftVal = float64(roc.Values.Left().(float64))
}

/*
	RECEIVER:
		-> roc (*RateOfChange): rateOfChange object to calculate value for
	ARGS:
		-> N/A
    RETURN:
        -> (float64): the current value for the given rateOfChange indicator
    WHAT:
		-> calculates rateOfChange for the values contained within the indicator's data queue
*/
func (roc *RateOfChange) GetVal() float64 {
	return (roc.RightVal - roc.LeftVal) / roc.LeftVal
}

// holds the SMA indicator
// SMA = SUM(values) / LEN(values)
type SMA struct {
	Values *deque.Deque // queue for storing values to compute SMA for
	MaxLen int          // stores the maximum lenth of the queue (period of the indicator)
	CurSum float64      // stores the current sum of the values in the queue
}

/*
	RECEIVER:
		-> sma (*SMA): SMA object to update
	ARGS:
		-> newVal (float64): new value to add to the indicator's data queue
    RETURN:
        -> N/A
    WHAT:
		-> puts the new value into the data queue and updates CurSum
*/
func (sma *SMA) Update(newVal float64) {
	// add the new value to the data queue and to the current sum
	sma.Values.PushRight(newVal)
	sma.CurSum += newVal

	// if the data queue is overfilled, pop the leftmost element and subtract it from the current sum
	if sma.Values.Size() > sma.MaxLen {
		removedVal := float64(sma.Values.PopLeft().(float64))
		sma.CurSum -= removedVal
	}
}

/*
	RECEIVER:
		-> sma (*SMA): SMA object to calculate value for
	ARGS:
		-> N/A
    RETURN:
        -> (float64): the current value for the given SMA indicator
    WHAT:
		-> calculates the SMA of the values contained within the indicator's data queue
*/
func (sma *SMA) GetVal() float64 {
	return sma.CurSum / math.Min(float64(sma.Values.Size()), float64(sma.MaxLen))
}
