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
    getCoinPositions
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
        self.volume = 0.0
        self.fees = 0.50



glob_status = GlobalStatus()
external_stylesheets = ["./assets/main.css"]

# Initialize Data Structures
container_statuses = dict()
for c in {'Portfolio Manager', 'Compute Engine', 'Data Consumer', 'Coinbase'}:
    container_statuses[c] = Status()

coin_datastreams = dict()
portfolio_datastream = DataStream(name='portfolio')

dc_conn = DCConnect()

cur_positions, position_history, plot_positions = retrieveDCData(dc_conn, coin_datastreams, portfolio_datastream, glob_status)
coins = list(coin_datastreams.keys())





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
    portfolio_datastream,
    plot_positions,
    ))



cb_socket_thread = threading.Thread(target=CBSocket, args=(
    glob_status,
    portfolio_datastream, 
    coin_datastreams,
    cur_positions,
    container_statuses['Coinbase'],
    coins))

dc_socket_thread.start() 
bh_socket_thread.start()
pm_socket_thread.start()

cb_socket_thread.start()


# Initialize Dash App
app = dash.Dash(__name__, title = "Trading Dashboard", update_title=None)

flask_server = app.server

app.layout = createPage(
        toptext = getTopText(portfolio_datastream.day_data, 'PORTFOLIO'),
        status_elems = getStatusElems(container_statuses), 
        position_elems = getPortfolioPositions(cur_positions.positions, position_history.all_positions),
        plot = getFig(portfolio_datastream.day_data),
        coins = coins,
        cur_coin='PORTFOLIO',
        volume=glob_status.volume,
        fees=glob_status.fees,
    )

# auth = dash_auth.BasicAuth(
#     app,
#     auth_pair
# )

@app.callback(Output('toptext_update', 'children'),
              Output('main_plot', 'figure'),
              Output('positions_update', 'children'),
              Output('status_update', 'children'),
              Output('volume', 'children'),
              Output('fees', 'children'),
              Input('auto_update', 'n_intervals'),
              State('session_data', 'data'))
def intervalUpdate(n, data):
    if data['asset']:
        asset = data['asset'].upper()
    else:
        asset = 'PORTFOLIO'
    timespan = data['timespan']
            
    if asset == 'PORTFOLIO':
        portfolio_data = portfolio_datastream.year_data
        if timespan == 'd':
            portfolio_data = portfolio_datastream.day_data
        elif timespan == 'w':
            portfolio_data = portfolio_datastream.week_data
        elif timespan == 'm':
            portfolio_data = portfolio_datastream.month_data

        return getTopText(portfolio_data, asset), getFig(portfolio_data), getPortfolioPositions(cur_positions.positions, position_history.all_positions), getStatusElems(container_statuses), f'${glob_status.volume}', f'{glob_status.fees}%'
    else:
        coin_data = coin_datastreams[asset].year_data
        coin_positions = plot_positions.positions_to_plot_year[asset]
        if timespan == 'd':
            coin_data = coin_datastreams[asset].day_data
            coin_positions = plot_positions.positions_to_plot_day[asset]
        elif timespan == 'w':
            coin_data = coin_datastreams[asset].week_data
            coin_positions = plot_positions.positions_to_plot_week[asset]
        elif timespan == 'm':
            coin_data = coin_datastreams[asset].month_data
            coin_positions = plot_positions.positions_to_plot_month[asset]
        return getTopText(coin_data, asset), getFig(coin_data, coin_positions), getCoinPositions(asset, cur_positions.positions[asset], position_history.coin_positions[asset]), getStatusElems(container_statuses), f'${glob_status.volume}', f'{glob_status.fees}%'


@app.callback(Output('session_data', 'data'),
              Output('d_button', 'style'),
              Output('w_button', 'style'),
              Output('m_button', 'style'),
              Output('y_button', 'style'),
              Input('dropdown', 'value'),
              Input('d_button', 'n_clicks'),
              Input('w_button', 'n_clicks'),
              Input('m_button', 'n_clicks'),
              Input('y_button', 'n_clicks'),
              Input('d_button', 'style'),
              Input('w_button', 'style'),
              Input('m_button', 'style'),
              Input('y_button', 'style'),
              State('session_data', 'data'))
def onEvent(value, d_clicks, w_clicks, m_clicks, y_clicks, d_style, w_style, m_style, y_style, data):
    ctx = dash.callback_context
    if len(ctx.triggered) > 1:
        return dash.no_update
    else:
        for trig in ctx.triggered:
            if trig['prop_id'] == 'dropdown.value':
                data['asset'] = trig['value']
            else:
                d_style, w_style, m_style, y_style = [{'font-weight': 'Normal', 'color': '#636567'}] * 4
                bold_style = {'font-weight': 'Bold', 'color': '#ebf5ff'}
                if trig['prop_id'] == 'd_button.n_clicks':
                    data['timespan'] = 'd'
                    d_style = bold_style
                elif trig['prop_id'] == 'w_button.n_clicks':
                    data['timespan'] = 'w'
                    w_style = bold_style
                elif trig['prop_id'] == 'm_button.n_clicks':
                    data['timespan'] = 'm'
                    m_style = bold_style
                elif trig['prop_id'] == 'y_button.n_clicks':
                    data['timespan'] = 'y'
                    y_style = bold_style
        return data, d_style, w_style, m_style, y_style
# @app.callback(Output('container_statuses', 'children'),
#               Input('auto_update', 'n_intervals'))
# def updateStatus(n):
#     return getStatusElems(container_statuses)

if __name__ == '__main__':
    print('Starting local WSGI server')
    app.run_server(host='0.0.0.0', port=8050, debug=False, dev_tools_silence_routes_logging=False)