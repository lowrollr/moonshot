package main

import (
	//"alert"

	"context"
	"time"
)

func userDataStream() {
	for {
		//start user stream and then subsequently continue to update so we have stream
		listenKey, err := binanceClinet.NewStartUserStreamService().Do(context.Background())
		if err != nil {
			panic(err)
		}

		for i := 0; i < 48; i++ {
			time.Sleep(30 * time.Minute)
			err = binanceClinet.NewKeepaliveUserStreamService().ListenKey(listenKey).Do(context.Background())
			if err != nil {
				panic(err)
			}
		}
		time.Sleep(24 * time.Hour)
	}
}
