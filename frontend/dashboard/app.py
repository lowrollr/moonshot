from data import (
    DataStream,
    Positions,
    PositionStream,
    Status
)
from client import (
    PMSocket,
    BHSocket,
    DCSocket,
    getCoins,
    startInit
)
from page import (
    createPage,
    getTopText,
    getFig,
    getStatusElems,
    getPortfolioPositions,
    getCoinPositions
)
import threading
import json
import dash
import time
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

# First, we'll initialize some data structures. 
# Then, we'll initialize some socket-listening threads.
# Finally, we'll initialize the Dash App.

external_stylesheets = ["./assets/main.css"]

# Initialize Data Structures
container_statuses = dict()
for c in {'PSM', 'Beverly Hills', 'Data Consumer', 'Binance'}:
    container_statuses[c] = Status()
#PRETEND WE GET THE COINS HERE
#TODO actually get the coins
dc_conn, coins = getCoins()
print(coins)
coin_datastreams = dict()
for coin in coins:
    coin_datastreams[coin] = DataStream(name=coin)

porfolio_datastream = DataStream(name='portfolio')
cur_positions = Positions(coins)
position_history = PositionStream(coins)



dc_socket_thread = threading.Thread(target=DCSocket, args=(
        dc_conn,
        container_statuses['Data Consumer'], 
        coin_datastreams,))

bh_socket_thread = threading.Thread(target=BHSocket, args=(container_statuses['Beverly Hills'],))

psm_socket_thread = threading.Thread(target=PMSocket, args=(
    container_statuses['PSM'], 
    porfolio_datastream,
    position_history.all_positions,
    position_history.coin_positions,
    cur_positions.positions,
    ))

dc_socket_thread.start() 
bh_socket_thread.start()
psm_socket_thread.start()



# Initialize Dash App
app = dash.Dash(__name__)

app.layout = createPage(
        toptext = getTopText(porfolio_datastream.day_data, 'FSC'),
        status_elems = getStatusElems(container_statuses), 
        position_elems = getPortfolioPositions(cur_positions.positions),
        plot = getFig(porfolio_datastream.day_data)
    )


@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def displayPage(pathname):
    if pathname == '/portfolio':
        return createPage(
                toptext = getTopText(porfolio_datastream.day_data, 'FSC'),
                status_elems = getStatusElems(container_statuses), 
                position_elems = getPortfolioPositions(cur_positions.positions),
                plot = getFig(porfolio_datastream.day_data)
            )
    else:
        coin = pathname[1:].upper()
        return createPage(
                toptext = getTopText(coin_datastreams[coin].day_data, coin),
                status_elems = getStatusElems(container_statuses), 
                position_elems = getCoinPositions(coin, cur_positions.positions),
                plot = getFig(coin_datastreams[coin].day_data)
            )


@app.callback(Output('container_statuses', 'children'),
              Input('auto_update', 'n_intervals'))
def updateStatus(n):
    return getStatusElems(container_statuses)

@app.callback(Output('container_statuses', 'children'),
              Input('auto_update', 'n_intervals'))
def updateStatus(n):
    return getStatusElems(container_statuses)

if __name__ == '__main__':
    
    app.server.run(host='192.168.75.216', port=1337)