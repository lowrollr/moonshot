package main

import (
	"fmt"
	"log"
	"time"

	"github.com/jinzhu/gorm"
	_ "github.com/jinzhu/gorm/dialects/postgres"
)

type dumbo struct{}

var (
	Dumbo = &dumbo{}
)

var global_db *gorm.DB

func (*dumbo) connectDB(database string) (*gorm.DB, error) {
	const timeout = 1 * time.Minute
	tries := 0

	deadline := time.Now().Add(timeout)
	for tries = 0; time.Now().Before(deadline); tries++ {
		fmt.Println("dbType")
		db, err := gorm.Open(dbType, database)
		if err == nil {
			global_db = db
			return db, nil
		}
		log.Printf("Could not connec to the database (%s). Retrying...", err.Error())
		time.Sleep(time.Second << uint(tries))
	}
	//Sleep for two seconds
	time.Sleep(2 * time.Second)
	return nil, fmt.Errorf("Failed to connect to the database of %d attempts", tries)
}

func (*dumbo) autoMigrate(database *gorm.DB) error {
	return database.AutoMigrate(&HistoricalCrypto{}, &CurrentCryptoPrice{},
		&CryptoNames{}, &PortfolioManager{}).Error
}

func (*dumbo) addConstraint(database *gorm.DB) error {
	err := database.Exec("ALTER TABLE sentiments DROP CONSTRAINT IF EXISTS source_id;").Error
	if err != nil {
		return err
	}
	err = database.Exec("ALTER TABLE sentiments ADD CONSTRAINT source_id " +
		" UNIQUE (data_stream, unique_id);").Error
	if err != nil {
		return err
	}

	err = database.Exec("ALTER TABLE stocks DROP CONSTRAINT IF EXISTS unique_stock_point;").Error
	if err != nil {
		return err
	}
	return database.Exec("ALTER TABLE stocks ADD CONSTRAINT " +
		"unique_stock_point UNIQUE (symbol, timestamp);").Error
}

//Have to change a bunch of this to match crypto stuff
// func (*dumbo) stock_crypto(crypto_data CryptoPayload) (Crypto, error) {
// 	stored_crypto := Crypto{Symbol: crypto_data.CompanySymbol,
// 		Price:     crypto_data.Price,
// 		Timestamp: crypto_data.DateTime}
// 	err := db.Create(&stored_crypto).Error
// 	return stored_crypto, err
// }

//dunno if we will be getting multiple crypto data points. Need to check
// func (*dumbo) many_stock_store(many_stock_data *[]CryptoPayload) error {
// 	var err error
// 	fmt.Println(many_stock_data)
// 	//fmt.Println(*many_sentiment_data[0])
// 	for _, stock := range *many_stock_data {
// 		err = global_db.Create(&Crypto{
// 			Symbol:    strings.ToLower(stock.CompanySymbol),
// 			Price:     stock.Price,
// 			Timestamp: stock.DateTime,
// 			Volume:    stock.Volume,
// 		}).Error
// 	}
// 	return err
// }

//maybe will need this
func (*dumbo) store_ticker_name(coin CryptoNames) error {
	return global_db.Create(&coin).Error
}

//also would need this for frontend possibly
// func (*dumbo) getTickerNames() (map[string]string, error) {
// 	var db_names []TickerName
// 	err := global_db.Find(&db_names).Error
// 	if err != nil {
// 		return map[string]string{}, err
// 	}
// 	comp_names := map[string]string{}
// 	for _, comp := range db_names {
// 		comp_names[comp.Ticker] = comp.Name
// 	}
// 	return comp_names, nil
// }
