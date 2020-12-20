package alert

import (
	"fmt"
	"strings"
	"net/http"
	"net/url"
	"encoding/json"
	"os"
  )

func sendAlertMessage(mesg string) {
	// Set account keys & information
	accountSid := os.Getenv("ACCOUNTSID")
	authToken := os.Getenv("AUTHTOKEN")
	urlStr := "https://api.twilio.com/2010-04-01/Accounts/" + accountSid + "/Messages.json"

	// Pack up the data for our message
	msgData := url.Values{}
	msgData.Set("To","+19135341422")
	msgData.Set("From","+12054797409")
	msgData.Set("Body",mesg)
	msgDataReader := *strings.NewReader(msgData.Encode())

	// Create HTTP request client
	client := &http.Client{}
	req, _ := http.NewRequest("POST", urlStr, &msgDataReader)
	req.SetBasicAuth(accountSid, authToken)
	req.Header.Add("Accept", "application/json")
	req.Header.Add("Content-Type", "application/x-www-form-urlencoded")

	// Make HTTP POST request and return message SID
	resp, _ := client.Do(req)
	if (resp.StatusCode >= 200 && resp.StatusCode < 300) {
	  var data map[string]interface{}
	  decoder := json.NewDecoder(resp.Body)
	  err := decoder.Decode(&data)
	  if (err == nil) {
		fmt.Println(data["sid"])
	  }
	} else {
		var data map[string]interface{}
	  decoder := json.NewDecoder(resp.Body)
	  _ = decoder.Decode(&data)
		fmt.Println(data)
	  fmt.Println(resp.Status)
	}
}

func TestInclude() {
	fmt.Println("heeeey")
}
