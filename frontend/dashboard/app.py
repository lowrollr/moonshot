from . import (
    DataStream, 
    Status, 
    Position, 
    PositionStream, 
    CurrentPositions, 
    dashboard, 
    coin_data, 
    getStatusDiv, 
    createPage, 
    getStatusElems, 
    getFig,
    getPositionElems,
    getTopText,
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
positions = dict()
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

#Initialize Threads



# Initialize Dash App
app = dash.Dash(__name__)


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


