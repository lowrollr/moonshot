from data import (
    DataStream,
    Positions,
    PositionStream,
    Status, 
    PlotPositions
)
from client import (
    PMSocket,
    BHSocket,
    DCSocket,
    retrieveDCData,
    startInit,
    PMConnect,
    DCConnect,
    BHConnect,
    CBSocket
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
import dash_auth
import json
import os
import dash
import time
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

auth_pair = {
    os.environ['AUTHUSER']:os.environ['AUTHPASS'],
}

# First, we'll initialize some data structures. 
# Then, we'll initialize some socket-listening threads.
# Finally, we'll initialize the Dash App.

class GlobalStatus:
    def __init__(self):
        self.isPaperTrading = False
        self.lastTimestampReceived = 0



glob_status = GlobalStatus()
external_stylesheets = ["./assets/main.css"]

# Initialize Data Structures
container_statuses = dict()
for c in {'Portfolio Manager', 'Compute Engine', 'Data Consumer', 'Coinbase'}:
    container_statuses[c] = Status()

coin_datastreams = dict()

dc_conn = DCConnect()
retrieveDCData(dc_conn, coin_datastreams, glob_status)
coins = list(coin_datastreams.keys())

porfolio_datastream = DataStream(name='portfolio')
cur_positions = Positions(coins)
position_history = PositionStream(coins)
plot_positions = PlotPositions(coins)



pm_conn = PMConnect()
bh_conn = BHConnect()

dc_socket_thread = threading.Thread(target=DCSocket, args=(
    glob_status,
    dc_conn,
    container_statuses['Data Consumer'], 
    coin_datastreams,
    cur_positions,
    ))

bh_socket_thread = threading.Thread(target=BHSocket, args=(container_statuses['Compute Engine'], bh_conn))

pm_socket_thread = threading.Thread(target=PMSocket, args=(
    glob_status,
    pm_conn,
    container_statuses['Portfolio Manager'],
    position_history.all_positions,
    position_history.coin_positions,
    cur_positions,
    porfolio_datastream,
    plot_positions,
    ))



cb_socket_thread = threading.Thread(target=CBSocket, args=(
    glob_status,
    porfolio_datastream, 
    coin_datastreams,
    cur_positions,
    container_statuses['Coinbase'],
    coins))

dc_socket_thread.start() 
bh_socket_thread.start()
pm_socket_thread.start()

cb_socket_thread.start()


# Initialize Dash App
app = dash.Dash(__name__)
flask_server = app.server

app.layout = createPage(
        toptext = getTopText(porfolio_datastream.day_data, 'PORTFOLIO'),
        status_elems = getStatusElems(container_statuses), 
        position_elems = getPortfolioPositions(cur_positions.positions),
        plot = getFig(porfolio_datastream.day_data),
        coins = coins,
        cur_coin='PORTFOLIO',
    )

# auth = dash_auth.BasicAuth(
#     app,
#     auth_pair
# )

@app.callback(Output('page-content', 'children'),
              Output('session_data', 'data'),
              Input('auto_update', 'n_intervals'),
              Input('dropdown', 'value'),
              State('session_data', 'data'))
def intervalUpdate(n, value, data):
    
    ctx = dash.callback_context
    if not data:
        data = dict()
        data['asset'] = 'PORTFOLIO'
        data['timespan'] = 'd'
    for trig in ctx.triggered:
        if trig['prop_id'] == 'dropdown.value':
            data['asset'] = trig['value']

    asset = data['asset'].upper()
    timespan = data['timespan']
            
    if asset == 'PORTFOLIO':
        return createPageContent(
            toptext = getTopText(porfolio_datastream.day_data, asset),
            status_elems = getStatusElems(container_statuses), 
            position_elems = getPortfolioPositions(cur_positions.positions),
            plot = getFig(porfolio_datastream.day_data),
            coins=coins,
            cur_coin=asset,
        ), data
    else:
        return createPageContent(
                toptext = getTopText(coin_datastreams[asset].day_data, asset),
                status_elems = getStatusElems(container_statuses), 
                position_elems = getCoinPositions(asset, cur_positions.positions[asset]),
                plot = getFig(coin_datastreams[asset].day_data, plot_positions.positions_to_plot_day[asset]),
                coins=coins,
                cur_coin=asset,
            ), data




# @app.callback(Output('container_statuses', 'children'),
#               Input('auto_update', 'n_intervals'))
# def updateStatus(n):
#     return getStatusElems(container_statuses)

if __name__ == '__main__':
    print('Starting local WSGI server')
    app.run_server(host='0.0.0.0', port=8050, debug=False, dev_tools_silence_routes_logging=False)