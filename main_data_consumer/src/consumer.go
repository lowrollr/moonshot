/*
FILE: consumer.go
AUTHORS:
    -> Ross Copeland <rhcopeland101@gmail.com>
WHAT:
	-> Code for actual consumption of data from bianance
	-> This will collect all information on coins (price, volume, time)
*/
package main

import (
	"os/exec"
	"strings"
	"time"

	log "github.com/sirupsen/logrus"
)

func printNumSockets() {
	command := "netstat -penut | grep ESTABLISHED | wc -l"
	out, err := exec.Command("sh", "-c", command).Output()
	if err != nil {
		panic(err)
	}
	// netstat_out, _ := exec.Command("netstat -penut").Output()
	// log.Println("testing netstat: " + strings.TrimSpace(string(netstat_out)))
	log.Println("\n\nNumber of sockets in use: " + strings.TrimSpace(string(out)))
}

/*
	ARGS:
		-> partition (int): < 5. how many times per minute you want to receive data
			-> binance does not allow for larger than 5
		-> prev_time (time.Time) at what time data was received to compute how long to wait
    RETURN:
        -> N/A
    WHAT:
		-> Waits the partition time but only that long and no longer
		-> Makes sure it does not wait less than partition so that IP is not blocked from binance
		-> Partition time is part of one second ex: 1/2 minute, 1/3 minute etc.
*/
func EfficientSleep(partition int, prev_time time.Time, duration time.Duration) {
	prev_time_nano := int64(prev_time.UnixNano())
	later_nano := int64(time.Now().UnixNano())
	partition_nano := duration.Nanoseconds() / int64(partition)
	if prev_time_nano-(later_nano-prev_time_nano) > 0 {
		time.Sleep(time.Duration(partition_nano-(later_nano-prev_time_nano)) * time.Nanosecond)
	}
}

/*
	ARGS:
        -> err (error) the error that was received
    RETURN:
        -> N/A
    WHAT:
		-> Function used in other functions to determine how errors should be handled
		-> ATM it is just panicing
    TODO:
		-> Should have a better way to deal with errors, some sort of logging,
			diagnostic, restart service, etc
*/
func ErrorTradeHandler(err error) {
	log.Warn("There error encountered " + err.Error())
	log.Warn(err)
}

/*
	ARGS:
		-> N/A
	RETURN:
        -> N/A
    WHAT:
		-> Needs some goroutine to constantly be doing something, hence the busy loop here
*/
func waitFunc() {
	for {
		time.Sleep(10 * time.Second)
		printNumSockets()
	}
}
