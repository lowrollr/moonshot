from data import (
    DataStream,
    Positions,
    PositionStream,
    Status
)
from client import (
    PMSocket,
    BHSocket,
    DCSocket
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
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

# First, we'll initialize some data structures. 
# Then, we'll initialize some socket-listening threads.
# Finally, we'll initialize the Dash App.

# Initialize Data Structures

container_statuses = dict()
for c in {'PSM', 'Beverly Hills', 'Data Consumer', 'Binance'}:
    container_statuses[c] = Status()
#PRETEND WE GET THE COINS HERE
#TODO actually get the coins
coins = ['BTC']

coin_datastreams = dict()
for coin in coins:
    coin_datastreams[coin] = DataStream(name=coin)

porfolio_datastream = DataStream(name='portfolio')
cur_positions = Positions(coins)
position_history = PositionStream(coins)

#Initialize Threads
threads = []
psm_socket_thread = threading.Thread(target=PMSocket, args=(
    container_statuses['PSM'], 
    porfolio_datastream,
    position_history.all_positions,
    position_history.coin_positions,
    cur_positions.positions,
    ))

bh_socket_thread = threading.Thread(target=BHSocket, args=(container_statuses['Beverly Hills'],))

dc_socket_thread = threading.Thread(target=DCSocket, args=(
    container_statuses['Data Consumer'], 
    coin_datastreams,))

dc_socket_thread.start()
bh_socket_thread.start()
psm_socket_thread.start()

# Initialize Dash App
app = dash.Dash(__name__)

app.layout = createPage(
    getTopText(porfolio_datastream, 'day', 'FSC'), 
    getFig(porfolio_datastream, 'day'), 
    getPositionElems(cur_positions), 
    getStatusElems(container_statuses)
    )


@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def displayPage(pathname):
    if pathname == '/portfolio':
        return createPage(
            
            toptext = getTopText('portfolio'),
            status_elems = getStatusElems(container_statuses), 
            position_elems = getPositionElems('portfolio'),
            plot = getFig('portfolio'))


    else:
        coin = pathname[1:].upper()



@app.callback(Output('container_statuses', 'children'),
              Input('auto_update', 'n_intervals'))
def updateStatus(n):
    return getStatusElems(container_statuses)

@app.callback(Output('container_statuses', 'children'),
              Input('auto_update', 'n_intervals'))
def updateStatus(n):
    return getStatusElems(container_statuses)

if __name__ == '__main__':
    app.run_server(debug=True)