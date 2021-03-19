/*
FILE: pm.go
AUTHORS:
	-> Jacob Marshall <marshingjay@gmail.com>
	-> Ross Copeland <rhcopeland101@gmail.com>
WHAT:
	-> This file contains all functionality and utility functions for maintaining the portfolio state and executing trades/ processing signals
*/

package main

import (
	"math"
	"os"
	"sort"
	"strconv"
	"strings"
	"time"

	coinbasepro "github.com/preichenberger/go-coinbasepro"
	decimal "github.com/shopspring/decimal"
	log "github.com/sirupsen/logrus"
	"gopkg.in/karalabe/cookiejar.v2/collections/deque"
)

// holds trade history for a given coin, and cumulitive metrics to make calculating averages faster
type ProfitQueue struct {
	Results *deque.Deque // queue object that holds trade results (profit amnt as percentage)
	SumOvr  float64      // total sum of all items in the queue
	SumPos  float64      // total sum of positive items in the queue
	SumNeg  float64      // total sum of negative items in the queue
	NumPos  int          // number of positive items in the queue
	NumNeg  int          // number of negative items in the queue
	NumOvr  int          // total number of items in the queue
}

// holds information pretaining to an asset being traded
type CoinInfo struct {
	InPosition       bool            // tracks if we have a position in this asset
	EnterPrice       decimal.Decimal // the price we last entered a position in this asset at
	EnterPriceFl     float64         // the price we last entered a position in this asset at (stored as a float)
	AmntOwned        decimal.Decimal // the amount of this asset that we currently own
	CashInvested     float64         // the amount of USD we spent to enter our last position in this asset
	ProfitHistory    *ProfitQueue    // ProfitQueue for storing trade history for this asset
	AvgProfit        float64         // average profit for trades in this asset's trade history
	WinRate          float64         // win rate (how often we make a winning trade) for this asset's trade history
	AvgWin           float64         // the average profit percentage when we make a winning trade (positive)
	AvgLoss          float64         // the average profit percentage when we make a losing trade (negative)
	IntermediateCash float64         // the amount of cash we've accrued so far by partially exiting our last position (useful for calculating profit when completely exiting)
	CoinOrderBook    *OrderBook      // the current live order book for this asset
	BidLiquidity     *SMA            // a moving average of liquidity snapshots for bids
	AskLiquidity     *SMA            // a moving average of liquidity snapshots for asks
}

// holds information concerning the state of the Portfolio Manager
type PortfolioManager struct {
	Volume            float64                    // current cumulitive volume (only used for paper trading)
	MakerFee          float64                    // current maker fee amount (only used for paper trading)
	TakerFee          float64                    // current taker fee amount (only used for paper trading)
	Strat             *Atlas                     // the strategy that the PM will be using to make trades
	ClientConnections map[string]*Client         // map of client names to websocket connections
	FrontendSocket    *ServerClient              // frontend socket server client
	CoinDict          map[string]*CoinInfo       // map of coin/asset names to CoinInfo objects
	Coins             *[]string                  // list of coins/assets being traded
	FreeCash          float64                    // amount of cash currently available for our portfolio to trade with (cash not locked up in an open position)
	PortfolioValue    float64                    // current unrealized value of the portfolio (incl. open positions)
	CoinbaseClient    *coinbasepro.Client        // coinbase websocket client
	TradesToCalibrate int                        // amount of trades needed before kelly criterion is used to determine allocation size
	CandleDict        map[string]CandlestickData // maps coins/assets to their most recently received candlesticks
	IsPaperTrading    bool                       // tracks if we are paper trading (true) or live trading (false)
	TargetSlippage    float64                    // the maximum amount of slippage to allow for when calculating liquidity
}

/*
	ARGS:
		-> N/A
    RETURN:
        -> pm (*Porfolio Manager): an initialized PortfolioManager object
    WHAT:
		-> initializes the portfolio manager
		-> connects to coinbase, retrieves & stores account information
		-> initializes CoinInfo objects for each coin
*/
func initPM() *PortfolioManager {
	// declate amount of trades necessary to compute allocation size with kelly criterion
	trades_to_cal := 10

	// initialize database connection
	Dumbo.InitializeDB()

	// initialize websocket clients
	mapDomainConnection := StartClients()

	// retrieve previous data from main data consumer to fill data queues
	coins, open_position_trades, prev_candles, prev_profits := mapDomainConnection[domainToUrl["main_data_consumer"]].GetPreviousData("main_data_consumer", trades_to_cal)
	log.Println(coins)
	// initialize strategy
	strategy := initAtlas(coins)

	// initialize coinbase connection
	client := coinbasepro.NewClient()

	//initialize candlestick map
	candleDict := make(map[string]CandlestickData)

	// initialize CoinInfo objects for each coin
	coinInfoDict := make(map[string]*CoinInfo)
	for _, coin := range *coins {
		coinInfoDict[coin] = &CoinInfo{
			InPosition:   false,
			EnterPrice:   decimal.NewFromFloat(0.0),
			EnterPriceFl: -1.0,
			AmntOwned:    decimal.NewFromFloat(0.0),
			ProfitHistory: &ProfitQueue{
				Results: deque.New(),
				SumNeg:  0,
				SumPos:  0,
				SumOvr:  0,
				NumOvr:  0,
				NumPos:  0,
				NumNeg:  0,
			},
			AvgProfit:        0.0,
			WinRate:          0.0,
			AvgWin:           0.0,
			AvgLoss:          0.0,
			IntermediateCash: 0.0,
			CoinOrderBook:    nil,
			AskLiquidity: &SMA{
				Values: deque.New(),
				MaxLen: 60,
				CurSum: 0,
			},
			BidLiquidity: &SMA{
				Values: deque.New(),
				MaxLen: 60,
				CurSum: 0,
			},
		}
		// store profit history retrieved from database
		for _, profit := range (*prev_profits)[coin] {
			coinInfoDict[coin].ProfitHistory.Results.PushRight(profit)
		}
	}

	// initialize PortfolioManager object
	pm := &PortfolioManager{
		ClientConnections: mapDomainConnection,
		CoinDict:          coinInfoDict,
		Coins:             coins,
		FreeCash:          0.0,
		PortfolioValue:    0.0,
		CoinbaseClient:    client,
		TradesToCalibrate: trades_to_cal,
		Strat:             strategy,
		MakerFee:          0.005,
		TakerFee:          0.005,
		Volume:            0.0,
		CandleDict:        candleDict,
		IsPaperTrading:    false,
		TargetSlippage:    0.0005, // target 0.05% slippage when calculating order book liquidity
	}

	// check environment variable that determines whether or not  we are paper trading
	if os.Getenv("PAPERTRADING") == "1" {
		log.Println("PM is paper trading!")
		pm.IsPaperTrading = true
	}

	// retrieve necessary account information from coinbase if we are not paper trading
	if !pm.IsPaperTrading {
		accounts, err := client.GetAccounts()
		if err != nil {
			println(err.Error())
		}
		fees, err := client.GetFees()
		if err != nil {
			log.Println("Error fetching account fees!")
		} else {
			pm.MakerFee, _ = strconv.ParseFloat(fees.MakerFeeRate, 64)
			pm.TakerFee, _ = strconv.ParseFloat(fees.TakerFeeRate, 64)
		}
		for _, a := range accounts {
			// is account USD
			currency := a.Currency
			if currency == "USD" {
				cashAvailable, err := strconv.ParseFloat(a.Available, 64)
				if err == nil {
					pm.FreeCash = cashAvailable
				}
				portfolioValue, err := strconv.ParseFloat(a.Balance, 64)
				if err == nil {
					pm.PortfolioValue = portfolioValue
				}

			} else {
				open_trades := (*open_position_trades)[currency]
				if len(open_trades) > 0 {
					
					entry_trade := open_trades[len(open_trades) - 1]
					log.Println(currency, " entry: ", entry_trade)
					pm.CoinDict[currency].InPosition = true
					pm.CoinDict[currency].CashInvested = entry_trade.ExecutedValue + entry_trade.Fees
					pm.CoinDict[currency].EnterPrice = decimal.NewFromFloat(entry_trade.ExecutedValue).Div(decimal.NewFromFloat(entry_trade.Units))
					pm.CoinDict[currency].EnterPriceFl, _ = pm.CoinDict[currency].EnterPrice.Float64()
					pm.CoinDict[currency].AmntOwned = decimal.NewFromFloat(entry_trade.Units)
				}
				for i := 0; i < len(open_trades) - 1; i++ {
					log.Println(currency, " partial exit: ", open_trades[i])
					pm.CoinDict[currency].IntermediateCash += open_trades[i].ExecutedValue
					pm.CoinDict[currency].AmntOwned = pm.CoinDict[currency].AmntOwned.Sub(decimal.NewFromFloat(open_trades[i].Units))
				}
			}
		}
		// otherwise initialize the porfolio cash
	} else {
		pm.PortfolioValue = 30000.00
		pm.FreeCash = 30000.00
		pm.Volume = 0.0
		pm.calcFees()
	}

	for _, coin := range *pm.Coins {
		
		// process previous data retrieved from database (fills up data queues in strategy object)
		for _, candle := range (*prev_candles)[coin] {
			strategy.Process(candle, coin)
		}
	}

	// send start messages to beverly hills and data consumer websocket  servers
	mapDomainConnection[domainToUrl["beverly_hills"]].StartRemoteServer("beverly_hills")
	mapDomainConnection[domainToUrl["main_data_consumer"]].StartRemoteServer("main_data_consumer")

	// store websocket connections
	pm.ClientConnections = mapDomainConnection

	// return initialized pm object
	return pm
}

/*
	RECEIVER:
		-> pm (*Portfolio Manager): Portfolio Manager object
	ARGS:
		-> N/A
    RETURN:
        -> N/A
    WHAT:
		-> main loop for trading
		-> waits to receive new set of candlestick data from data consumer, reads/stores that data, then calls PMProcess to execute strategy methods on that data
		-> updates liquidity and unrealized portfolio value every iteration
*/
func (pm *PortfolioManager) StartTrading() {
	time.Sleep(5 * time.Second)
	// get initial unrealized portfolio value & liqudity
	pm.PortfolioValue = pm.CalcPortfolioValue()
	pm.UpdateLiquidity()
	
	// loop forever
	for {
		// wait for new data to arrive
		newCandleData := *pm.ClientConnections[domainToUrl["main_data_consumer"]].ReceiveCandleData()
		// if there is data, process it
		if len(newCandleData) > 0 {
			for _, coin := range *pm.Coins {
				candles := newCandleData[coin]
				for _, candle := range candles {
					pm.CandleDict[coin] = candle
					pm.Strat.Process(candle, coin)

				}
			}
			pm.PMProcess()
		}
		// update portfolio value & liquidity
		pm.PortfolioValue = pm.CalcPortfolioValue()
		pm.UpdateLiquidity()
	}

}

/*
	RECEIVER:
		-> pm (*Portfolio Manager): Portfolio Manager object
	ARGS:
		-> N/A
    RETURN:
        -> N/A
    WHAT:
		-> processes Candlestick data to make trading decisions for each coin
		-> enters/exits positions according to signals from a strategy as well as with respect to PM policies
*/
func (pm *PortfolioManager) PMProcess() {

	// pass Candlestick data for each coin to the strategy object and check for buy/sell signals
	enter_coins := []string{}
	for _, coin := range *pm.Coins {

		// get the appropriate candlestick
		candle := pm.CandleDict[coin]

		// if we have a position in the given coin, see if the strategy tells us we should exit
		if pm.CoinDict[coin].InPosition {
			if pm.Strat.CalcExit(candle, coin) {
				// these signals are acted upon immediately no matter the PM state, so exit the position
				if pm.IsPaperTrading {
					pm.FreeCash += pm.paperExit(coin, pm.CoinDict[coin].AmntOwned)
				} else {
					pm.FreeCash += pm.exitPosition(coin, pm.CoinDict[coin].AmntOwned)
				}

			}
			// otherwise check for an enter signal
		} else {
			// we can't act on these signals immediately, these depend on portfolio state
			// append the coin to enter_coins if there is a signal, we'll choose which signals to enter once we've looked at every coin
			if pm.Strat.CalcEnter(candle, coin, pm.ClientConnections[domainToUrl["beverly_hills"]]) {
				enter_coins = append(enter_coins, coin)
			}
		}
	}

	// sort the list of enter signals according to how profitable trading each coin has historically been (most -> least)
	if len(enter_coins) > 0 {
		pm.SortByProfit(&enter_coins)
	}

	// iterate through the sorted list of enter signals and determine whether they should be acted upon
	for _, coin := range enter_coins {
		// calculate the allocation value
		allocation := CalcKellyPercent(pm.CoinDict[coin], pm.TradesToCalibrate)

		// determine how much USD this translates to
		cashToAllocate := pm.PortfolioValue * allocation

		// determine how much liquidity we currently estimate exists (avg of bid and ask liquidity SMAs)
		expLiquidity := (pm.CoinDict[coin].AskLiquidity.GetVal() + pm.CoinDict[coin].BidLiquidity.GetVal()) / 2

		// determine how much cash to allocate (capped by liquidity if necessary)
		cashToAllocate = math.Min(cashToAllocate, expLiquidity)

		// if our portfolio has enough liquid cash to open the position, open the position
		if cashToAllocate < pm.FreeCash {
			if pm.IsPaperTrading {
				pm.FreeCash -= pm.paperEnter(coin, cashToAllocate)
			} else {
				pm.FreeCash -= pm.enterPosition(coin, cashToAllocate)
			}
			// if not, determine if positions should be closed to make room
		} else {
			// get all coins in positions sorted by current profit (if closed right now)
			coinsInPosition := pm.GetCoinsInPosition(*pm.Coins)
			crMap := pm.SortByCurrentReturn(coinsInPosition)

			// examine each of these positions to determine whether we should close it to open the new position
			for _, coinIn := range *coinsInPosition {
				// if we have enough cash to open the new position, break
				if cashToAllocate <= pm.FreeCash {
					break
				}

				// check if the current open position is profitable
				if (*crMap)[coinIn] > 0 {
					// if it is, we want to close all or part of it
					amntOwnedStr := pm.CoinDict[coinIn].AmntOwned.String()
					amntOwnedFlt, _ := strconv.ParseFloat(amntOwnedStr, 64)
					curCashValue := (1 - pm.TakerFee) * pm.CandleDict[coinIn].Close * amntOwnedFlt
					cashNeeded := curCashValue - pm.FreeCash

					// close all of it if we need all or more of the cash than the position provides
					if cashNeeded >= curCashValue {
						if pm.IsPaperTrading {
							pm.FreeCash += pm.paperExit(coinIn, pm.CoinDict[coinIn].AmntOwned)
						} else {
							pm.FreeCash += pm.exitPosition(coinIn, pm.CoinDict[coinIn].AmntOwned)
						}
						// paritally close out the position if completely closing it out would give us more than enough cash
					} else {
						// calculate how much of the position (approximately) we need to close
						// note: this will never be exact (due to unknown slippage we'll incur) but will be pretty close
						amntToSell := (cashNeeded / curCashValue) * amntOwnedFlt
						if pm.IsPaperTrading {
							pm.FreeCash += pm.paperExit(coinIn, decimal.NewFromFloat(amntToSell))
						} else {
							pm.FreeCash += pm.exitPosition(coinIn, decimal.NewFromFloat(amntToSell))
						}
						break
					}
				} else {
					break
				}
			}
			// allocate cash equal to the allocated position size (or if we can't allocate that much, the amount of cash we have free)
			// and enter into the new position
			if pm.FreeCash > 0 {
				amntToAllocate := math.Min(pm.FreeCash, cashToAllocate)
				if pm.IsPaperTrading {
					pm.FreeCash -= pm.paperEnter(coin, amntToAllocate)
				} else {
					pm.FreeCash -= pm.enterPosition(coin, amntToAllocate)
				}
			}
		}
	}
}

/*
	ARGS:
		-> coin (string): coin/asset to check slice for
		-> slice (*[]string): slice to check if coin exists in (should be list of coins)
    RETURN:
        -> bool (): true if coin exists in slice, false if not
    WHAT:
		-> helper function to check if a certain coin is present in a list of coins
*/
func ExistsInSlice(coin string, slice *[]string) bool {
	for _, item := range *slice {
		if item == coin {
			return true
		}
	}
	return false
}

/*
	RECEIVER:
		-> pm (*Portfolio Manager): Portfolio Manager object
	ARGS:
		-> coins ([]string): list of coins
    RETURN:
        -> &coinsInPosition (*[]string): list of coins that are currently in a position
    WHAT:
		-> given a list of coins, returns a new list that contains only coins that currently have an open position
*/
func (pm *PortfolioManager) GetCoinsInPosition(coins []string) *[]string {
	coinsInPosition := []string{}
	for _, coin := range coins {
		if pm.CoinDict[coin].InPosition {
			coinsInPosition = append(coinsInPosition, coin)
		}
	}
	return &coinsInPosition
}

/*
	RECEIVER:
		-> pm (*Portfolio Manager): Portfolio Manager object
	ARGS:
		-> N/A
    RETURN:
        -> total_value (float64): the toal (unrealized) value of the portfolio
    WHAT:
		-> syncs our current cash balance with Coinbase
		-> then, calculates the current cash value of all positions we have open
		-> returns the sum of the two previous items
*/
func (pm *PortfolioManager) CalcPortfolioValue() float64 {

	// if we're not paper trading, fetch our current cash balance from Coinbase
	if !pm.IsPaperTrading {
		accounts, _ := pm.CoinbaseClient.GetAccounts()
		for _, a := range accounts {

			// find the 'USD' account and get its balance
			currency := a.Currency
			if currency == "USD" {
				cashAvailable, err := strconv.ParseFloat(a.Available, 64)
				if err == nil {
					pm.FreeCash = cashAvailable
				}
				break
			}
		}
	}
	// (if we are paper trading, then FreeCash will be up to date)
	// (it technically should be up to date for real trading as well, but good to sync up with coinbase's records just in case)
	total_value := pm.FreeCash

	// calculate the current cash value of each open position
	// add the sum of these to the portfolio's free cash
	for _, coin := range *pm.Coins {
		if pm.CoinDict[coin].InPosition {
			amntOwnedFlt, _ := strconv.ParseFloat(pm.CoinDict[coin].AmntOwned.String(), 64)
			total_value += amntOwnedFlt * pm.CandleDict[coin].Close
		}
	}

	// return the portfolio's current unrealized cash value
	return total_value
}

/*
	RECEIVER:
		-> pm (*Portfolio Manager): Portfolio Manager object
	ARGS:
		-> coins (*[]string): list of assets/coins we will examine
    RETURN:
        -> N/A
    WHAT:
		-> helper function to sort a list of coins by their average profit
		-> sorts the slice in-place
*/
func (pm *PortfolioManager) SortByProfit(coins *[]string) {
	sort.Slice(*coins, func(i, j int) bool {
		return pm.CoinDict[(*coins)[i]].AvgProfit > pm.CoinDict[(*coins)[j]].AvgProfit
	})
}

/*
	RECEIVER:
		-> pm (*Portfolio Manager): Portfolio Manager object
	ARGS:
		-> coins (*[]string): list of assets/coins we will examine
    RETURN:
        -> &crMap (*map[string]float64): maps coins to current return
    WHAT:
		-> helper function to sort a list of coins by their current return
		-> assumes the list of coins passed are all in positions
		-> sorts the slice in-place
		-> returns a map from coin to current return
*/
func (pm *PortfolioManager) SortByCurrentReturn(coins *[]string) *map[string]float64 {
	// create the coin -> current return map
	crMap := make(map[string]float64)
	for _, coin := range *coins {
		// calculate the current return for the given coin
		amntOwnedStr := pm.CoinDict[coin].AmntOwned.String()
		amntOwnedFlt, _ := strconv.ParseFloat(amntOwnedStr, 64)
		currentReturn := ((((pm.CandleDict[coin].Close * amntOwnedFlt) * (1 - pm.TakerFee)) + pm.CoinDict[coin].IntermediateCash) / pm.CoinDict[coin].CashInvested) - 1.0
		crMap[coin] = currentReturn
	}

	// sort the slice by current return
	sort.Slice(*coins, func(i, j int) bool {
		return crMap[(*coins)[i]] > crMap[(*coins)[j]]
	})

	// return the coin -> current return map
	return &crMap
}

/*
	RECEIVER:
		-> pm (*Portfolio Manager): Portfolio Manager object
	ARGS:
		-> coins (*[]string): list of assets/coins we will examine
    RETURN:
        -> &evMap (*map[string]float64): maps coins to current expected remaining value
    WHAT:
		-> helper function to sort a list of coins by their expected remaining value
		-> assumes the list of coins passed are all in positions
		-> sorts the slice in-place
		-> returns a map from coin to expected remaining value
*/
func (pm *PortfolioManager) SortByEV(coins *[]string) *map[string]float64 {
	// create the coin -> expected remaining value map
	evMap := make(map[string]float64)
	for _, coin := range *coins {
		// calculate the expected remaining value for the given coin
		amntOwnedStr := pm.CoinDict[coin].AmntOwned.String()
		amntOwnedFlt, _ := strconv.ParseFloat(amntOwnedStr, 64)
		// ERV = Avg. Win - Current Profit
		expectedValue := pm.CoinDict[coin].AvgWin - (((((pm.CandleDict[coin].Close * amntOwnedFlt) * (1 - pm.TakerFee)) + pm.CoinDict[coin].IntermediateCash) / pm.CoinDict[coin].CashInvested) - 1.0)
		evMap[coin] = expectedValue

	}

	// sort the slice of coins by expected remaing value
	sort.Slice(*coins, func(i, j int) bool {
		return evMap[(*coins)[i]] > evMap[(*coins)[j]]
	})

	// return the coin -> expected remaining value map
	return &evMap
}

/*
	ARGS:
		-> info (*CoinInfo): CoinInfo object we'll use to calculate Kelly allocation amount
		-> minTrades (float64): number of trades required in order to calculate Kelly allocation amount
    RETURN:
        -> kelly (float64): the Kelly allocation amount (or one of our default values if it's not possible to calculate yet)
    WHAT:
		-> calculates the optimal allocation amount using the Kelly Criterion
		-> read more: https://en.wikipedia.org/wiki/Kelly_criterion
		-> if there are not enough trades, return a defualt amount (5%)
		-> if the kelly criterion gives us a number less than or equal to zero, instead return a very small amount (0.05%)
*/
func CalcKellyPercent(info *CoinInfo, minTrades int) float64 {
	low_amnt := 0.001
	default_amnt := 0.05
	if info.ProfitHistory.Results.Size() >= minTrades {
		if info.AvgWin != 0.0 && info.AvgLoss != 0.0 {
			// use Kelly criterion equation to obtain optimal bet size
			kelly := info.WinRate - ((1 - info.WinRate) / (info.AvgWin / math.Abs(info.AvgLoss)))
			if kelly > 0 {
				return kelly
			} else {
				return low_amnt
			}
		} else if info.AvgWin > 0 {
			return 0.8
		} else if info.AvgLoss < 0 {
			return 0.001
		}

	}
	// return the calculated allocation amount
	return default_amnt
}

/*
	RECEIVER:
		-> pm (*Portfolio Manager): Portfolio Manager object
	ARGS:
		-> coin (string): the coin to enter a position in
		-> cashAllocated (float64): the amount of cash to allocate to the position
    RETURN:
        -> cashAllocated (float64): the amount of cash that was allocated to the position (equal to 0 or amount passed in)
    WHAT:
		-> places a market buy order for the given coin and updates its info accordingly if the order fills
		-> sends trade info to database
		-> sends trade message to frontend
*/
func (pm *PortfolioManager) enterPosition(coin string, cashAllocated float64) float64 {
	// create a market buy order for the given coin
	filledOrder := marketOrder(pm.CoinbaseClient, coin, decimal.NewFromFloat(cashAllocated), true)

	// grab the coin info object for the coin we entered a position in
	info := pm.CoinDict[coin]

	// if the order settles, updated the coin's CoinInfo object
	if filledOrder.Settled {
		info.InPosition = true
		info.CashInvested = cashAllocated
		// retrieve the execValue (cash size of trade (not including fees)), and filled size (amount of the coin we received)
		execValue, _ := decimal.NewFromString(filledOrder.ExecutedValue)
		fillSize, _ := decimal.NewFromString(filledOrder.FilledSize)
		// enter price = cash size of trade / amount of coin we received
		info.EnterPrice = execValue.Div(fillSize)
		enterPriceFl, _ := strconv.ParseFloat(info.EnterPrice.String(), 64)
		info.EnterPriceFl = enterPriceFl
		info.AmntOwned = fillSize

		feesDec, _ := decimal.NewFromString(filledOrder.FillFees)
		// store the trade in the database
		go Dumbo.StoreTrade(0, coin, fillSize, execValue, feesDec, pm.CandleDict[coin].Close, 0.0)

		// send a message to frontend with information about the opened position
		sendEnter(pm.FrontendSocket, coin, filledOrder.FilledSize, info.EnterPrice.String())

		// return the cash we spent on the position
		return cashAllocated

	} else {
		// if not, the order did not fill (for some reason), so no cash was used
		return 0.0
	}
}

/*
	RECEIVER:
		-> pm (*Portfolio Manager): Portfolio Manager object
	ARGS:
		-> coin (string): the coin to exit a position in
		-> portionToSell (decimal.Decimal): the amount of the position to sell (amount of asset units)
    RETURN:
        -> newCash (float64): the amount of cash we received from closing the position
    WHAT:
		-> places a market sell order for the given coin and updates its info accordingly if the order fills
		-> sends trade info to database
		-> sends trade message to frontend
*/
func (pm *PortfolioManager) exitPosition(coin string, portionToSell decimal.Decimal) float64 {
	// create a market sell order for the given coin
	filledOrder := marketOrder(pm.CoinbaseClient, coin, portionToSell, false)

	// grab the coin info object for the coin we exited our position in
	info := pm.CoinDict[coin]

	// if the order settles, updated the coin's CoinInfo object
	if filledOrder.Settled {
		// retrieve the execValue (cash size of trade (not including fees)), and filled size (amount of the coin we sold)
		fillSize, _ := decimal.NewFromString(filledOrder.FilledSize)
		execValue, _ := decimal.NewFromString(filledOrder.ExecutedValue)
		fees, _ := decimal.NewFromString(filledOrder.FillFees)
		newCash, _ := strconv.ParseFloat(execValue.Sub(fees).String(), 64)

		// if we did not sell all of our position, updated IntermediateCash (used for calculating total profit when we do completely close later)
		if portionToSell != info.AmntOwned {
			info.IntermediateCash += newCash
			info.AmntOwned = info.AmntOwned.Sub(portionToSell)
			// store the trade in the database
			go Dumbo.StoreTrade(1, coin, fillSize, execValue, fees, pm.CandleDict[coin].Close, 0.0)
		} else {
			// otherwise set the position to closed
			info.InPosition = false

			// calculate our profit and update the profit history
			profitPercentage := ((newCash + info.IntermediateCash) / info.CashInvested) - 1.0
			info.updateProfitInfo(profitPercentage)

			info.IntermediateCash = 0.0

			// store the trade in the database
			go Dumbo.StoreTrade(2, coin, fillSize, execValue, fees, pm.CandleDict[coin].Close, profitPercentage)

		}

		

		// send a message to frontend with information about the position we exited
		sendExit(pm.FrontendSocket, coin, portionToSell.String(), filledOrder.ExecutedValue)

		// return the amount of cash we received from closing the position
		return newCash
	} else {
		// if the order did not settle, no cash was received (no trade was made)
		return 0.0
	}
}

/*
	RECEIVER:
		-> info (*CoinInfo):  CoinInfo object to update profit results for
	ARGS:
		-> profitPercentage (float64): a new trade result
    RETURN:
        -> N/A
    WHAT:
		-> adds a new profit amount to the results queue and updates metrics (avgWin, avgLoss, etc.) accordingly
*/
func (info *CoinInfo) updateProfitInfo(profitPercentage float64) {
	// retrieve the profit queue object we want to update
	profitQueue := info.ProfitHistory

	// add the new profit percentage to the queue
	profitQueue.Results.PushRight(profitPercentage)

	// update the new overall sum with the new profit percentage, and increment the overall total number of trades
	profitQueue.SumOvr += profitPercentage
	profitQueue.NumOvr += 1

	// if the profit was positive, update the positive trade statistics (SumPos, NumPos)
	// otherwise, update the negative trade statistics (SumNeg, NumNeg)
	if profitPercentage > 0 {
		profitQueue.SumPos += profitPercentage
		profitQueue.NumPos += 1
	} else if profitPercentage < 0 {
		profitQueue.SumNeg += profitPercentage
		profitQueue.NumNeg += 1
	}

	// if the queue has gone over its max size, pop the leftmost element and update the totals accordingly
	if profitQueue.Results.Size() > 20 {
		// pop the leftmost element
		oldVal := float64(profitQueue.Results.PopLeft().(float64))

		// subtract that element from overall sum and decrement the total number of trades
		profitQueue.SumOvr -= oldVal

		// if the profit was positive, update the positive trade statistics (SumPos, NumPos)
		// otherwise, update the negative trade statistics (SumNeg, NumNeg)
		profitQueue.NumOvr -= 1
		if oldVal > 0 {
			profitQueue.SumPos -= oldVal
			profitQueue.NumPos -= 1
		} else {
			profitQueue.SumNeg -= oldVal
			profitQueue.NumNeg -= 1
		}
	}

	// calculate the new averages and win rate
	info.AvgLoss = profitQueue.SumNeg / float64(profitQueue.NumNeg)
	info.AvgWin = profitQueue.SumPos / float64(profitQueue.NumPos)
	info.AvgProfit = profitQueue.SumOvr / float64(profitQueue.NumOvr)
	info.WinRate = float64(profitQueue.NumPos) / float64(profitQueue.NumOvr)
}

/*
	RECEIVER:
		-> pm (*Portfolio Manager): Portfolio Manager object
	ARGS:
		-> initialized (chan bool): channel that is updated when all coins have an initialized order book
    RETURN:
        -> N/A
    WHAT:
		-> reads Coinbase order book socket and initializes/updates OrderBook objects for each coin accordingly
		-> lets main thread know when OrderBook objects are initialized via 'initialized' channel
*/
func (pm *PortfolioManager) ReadOrderBook(initialized chan bool) {
	// flag to track whether every coin's order book has been initialized
	fullyInitialized := false

	// number of coins that have been initialized so far
	coinsInitalized := 0

	// run this routine forever
	for {
		log.Println("Starting level2 order book socket initialization...")

		// connect to the Coinbase order book socket
		conn, err := ConnectToCoinbaseOrderBookSocket(pm.Coins)

		// if there was an error connecting, note the error
		if err != nil {
			log.Panic("Was not able to open websocket with error: " + err.Error())
		}

		// read the order book
		for {
			// create a message object to read into from socket
			message := CoinBaseMessage{}

			// read the socket
			if err := conn.ReadJSON(&message); err != nil {
				// if there was an error, close the connection and break out if the inner for loop
				// (the outer for loop will try to reconnect)
				log.Warn("Was not able to retrieve message with error: " + err.Error())
				conn.Close()
				log.Warn("Attempting to restart connection...")
				break
			}

			// if the message type is 'snapshot', initialize the orderBook for the appropriate coin
			if message.Type == "snapshot" {

				// parse the productID to get the coin string
				coin := strings.Split(message.ProductID, "-")[0]

				// initialize the order book if it hasn't been initialized yet
				if pm.CoinDict[coin].CoinOrderBook == nil {
					pm.CoinDict[coin].CoinOrderBook = InitOrderBook(&message.Bids, &message.Asks)

					// increment the number of coins that have been initialized
					coinsInitalized++

					// if every coin has been initialized, read 'true' into the channel (will allow main thread to continue)
					if coinsInitalized == len(*pm.Coins) && !fullyInitialized {
						fullyInitialized = true
						initialized <- true
					}
				} else {
					//  if the orderBook has already been initialized, we don't need to do anything with the channel
					// but we still want to reinitialize the order book
					// this will likely happen when reconnecting after an error/disconnect
					pm.CoinDict[coin].CoinOrderBook = InitOrderBook(&message.Bids, &message.Asks)
				}

				// if the message type is 'l2update', update the orderBook accordingly
			} else if message.Type == "l2update" {

				// parse the productID to get the coin string
				coin := strings.Split(message.ProductID, "-")[0]

				// update the orderbook with each order book change contained in the message
				for _, change := range message.Changes {
					if change[0] == "buy" {
						pm.CoinDict[coin].CoinOrderBook.Bids.Update(change[1], change[2])
					} else {
						pm.CoinDict[coin].CoinOrderBook.Asks.Update(change[1], change[2])
					}
				}

			} else if message.Type == "error" {
				// log the error if we get an error message from the socket
				log.Println(message)
			} else if message.Type != "subscriptions" {
				// restart the connection if we are getting a message type we do not expect
				log.Warn("Got wrong message type: " + message.Type)
				conn.Close()
				log.Warn("Attempting to restart connection...")
				break
			}
		}

	}
}
