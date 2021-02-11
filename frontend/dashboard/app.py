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
    getCoinPositions,
    createPageContent
)
import threading
import json
import dash
import time
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

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
        plot = getFig(porfolio_datastream.day_data),
        coins = coins
    )

@app.callback(Output('page-content', 'children'),
              Output('session_data', 'data'),
              Input('auto_update', 'n_intervals'),
              Input('dropdown', 'value'),
              State('session_data', 'data'))
def intervalUpdate(n, value, data):
    
    ctx = dash.callback_context
    if not data:
        data = dict()
        data['asset'] = 'portfolio'
        data['timespan'] = 'd'
    for trig in ctx.triggered:
        if trig['prop_id'] == 'dropdown.value':
            data['asset'] = trig['value']

    asset = data['asset'].upper()
    timespan = data['timespan']
            
    if asset == 'PORTFOLIO':
        return createPageContent(
            toptext = getTopText(porfolio_datastream.day_data, 'FSC'),
            status_elems = getStatusElems(container_statuses), 
            position_elems = getPortfolioPositions(cur_positions.positions),
            plot = getFig(porfolio_datastream.day_data),
            coins=coins
        ), data
    else:
        return createPageContent(
                toptext = getTopText(coin_datastreams[asset].day_data, asset),
                status_elems = getStatusElems(container_statuses), 
                position_elems = getCoinPositions(asset, cur_positions.positions[asset]),
                plot = getFig(coin_datastreams[asset].day_data),
                coins=coins
            ), data




# @app.callback(Output('container_statuses', 'children'),
#               Input('auto_update', 'n_intervals'))
# def updateStatus(n):
#     return getStatusElems(container_statuses)

if __name__ == '__main__':
    
    app.run_server(host='0.0.0.0', port=8050)