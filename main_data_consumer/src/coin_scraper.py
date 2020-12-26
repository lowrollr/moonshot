import requests
from bs4 import BeautifulSoup

url = "https://coinmarketcap.com/all/views/all/"

def write_to_csv(filename, data):
    pass

def main():
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    table = soup.find('tbody')

    all_coins = table.find_all('tr')

    coin_data = []
    for coin in all_coins:
        attr = coin.find_all('td')
        coin_data.append((attr[1].text, attr[2]))

    write_to_csv("../data/tracked_coins.csv", coin_data)

if __name__ == "__main__":
    main()
