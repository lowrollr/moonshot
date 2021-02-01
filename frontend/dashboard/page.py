import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from plotly.subplots import make_subplots


def createPage(toptext, plot, position_elems, status_elems):
    return html.Div([
        dcc.Interval(
            id='auto_update',
            interval=500,
            n_intervals=0
        ),
        html.Div(className='background'),
        html.Div(
            className='sidebar',
            children=[
                position_elems,
                status_elems
            ]
        ),
        html.Div(
            className='main',
            children=[
                toptext,
                dcc.Graph(
                    id='main_plot', 
                    className='plot',
                    
                    )
            ]
        )
    ])


#TODO: plot volume on secondary axis
#TODO: add timestamps to x axis & data points
def getPortfolioFig(portfolio_datastream, timespan):
    fig = make_subplots()
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)')
    
    indices, values = enumerate(list(portfolio_datastream))
    fig.add_trace(go.Scatter(x=indices, y=values))

    return fig


def getStatusElems(container_statuses):
    html.Ul(
        className='status_group',
        id='container_statuses',
        children=[
            html.Li([
                html.Div('PSM', className='statustext'),
                getStatusDiv(container_statuses['PSM'])
            ], className = 'statuspair'),
            html.Li([
                html.Div('Data Consumer', className='statustext'),
                getStatusDiv(container_statuses['Data Consumer'])
            ], className = 'statuspair'),
            html.Li([
                html.Div('PSM', className='statustext'),
                getStatusDiv(container_statuses['PSM'])
            ], className = 'statuspair'),
            html.Li([
                html.Div('Beverly Hills', className='statustext'),
                getStatusDiv(container_statuses['Beverly Hills'])
            ], className = 'statuspair'),
            html.Li([
                html.Div('Binance', className='statustext'),
                getStatusDiv(container_statuses['Binance'])
            ], className = 'statuspair'),
        ]
    )

def getStatusDiv(status, is_big):
    class_name = 'statusbubble'
    if is_big:
        class_name = 'statusbubble_big'
    # make this thread safe pls
    if status.isOk():
        html.Div(className=class_name, style={'color': 'rgba(114,228,125,1)'})
    else:
        return html.Div(className=class_name, style={'color': 'rgba(239,102,102,1)'})

# TODO: make this display past positions
def getPortfolioPositions(positions):
    elements = []
    for coin in positions[::-1]:
        cur_amnt = positions[coin]['amnt']
        cur_price = positions[coin]['price']
        profit = positions[coin]['profit']
        if profit > 0:
            profit = '+' + str(profit) + '%'
        else:
            profit = str(profit) + '%'
        alloc = positions[coin]['alloc']
        element = html.Li(
            className='position',
            children= f'{cur_amnt} {coin} / ${cur_price} {profit} / {alloc}'
        )
        elements.append(element)
    return html.Ul(
        className='position_list',
        children=elements
    )
        

# TODO: make this display past positions
def getCoinPositions(coin, cur_position):
    elements = []
    cur_amnt = cur_position['amnt']
    cur_price = cur_position['price']
    profit = str(cur_position['profit'])
    if profit > 0:
        profit = '+' + str(profit) + '%'
    else:
        profit = str(profit) + '%'
    alloc = cur_position['alloc']

    elements.append(html.Li(
        className = 'position',
        children = f'{cur_amnt} {coin} / ${cur_price} {profit} / {alloc}'
    ))

    return html.Ul(
        className='position_list',
        children=elements
    )