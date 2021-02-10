import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from plotly.subplots import make_subplots


def createPage(toptext, plot, position_elems, status_elems):
    return html.Div(children=[
        dcc.Interval(
            id='auto_update',
            interval=1000,
            n_intervals=0
        ),
        dcc.Location(id='url', refresh=False),
        dcc.Store(id='session_data', storage_type='session'),
        html.Div(
            id='page-content', 
            children=createPageContent(toptext, plot, position_elems, status_elems))
    ])
        

def createPageContent(toptext, plot, position_elems, status_elems):
    return [
        
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
                    figure=plot
                    )
            ]
        )
    ]

def getTopText(data, asset):
    
    cur_value = '$0.00'
    delta = '+$0.00'
    perc_change = '+0.00%'
    if data:
        cur_value = data[-1]
        first_value = data[0]
        delta = cur_value - first_value
        perc_change = (cur_value - first_value) / first_value
        cur_value = round(cur_value, 2)
        delta = round(delta, 2)
        perc_change = round(perc_change, 2)
        if delta >= 0:
            delta = f'+${delta}'
        else:
            delta = f'-${str(delta)[1:]}'
        
        if perc_change >= 0:
            perc_change = f'+{perc_change}%'
        else:
            perc_change = f'{perc_change}%'

        cur_value = f'${cur_value}'



    return html.Div(
        className='asset_info',
        children=[
            html.Span(
                className='asset_value',
                children=f'{asset} {cur_value}'
            ),
            html.Br(),
            html.Span(
                className='asset_delta',
                children=f'{perc_change} {delta}'
            )
        ]
    )


#TODO: plot volume on secondary axis
#TODO: add timestamps to x axis & data points
def getFig(datastream):
    fig = make_subplots()
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)')
    if datastream:
        indices, values = zip(*enumerate(list(datastream)))
        fig.add_trace(go.Scatter(x=indices, y=values))

    return fig




def getStatusElems(container_statuses):
    all_ok = True
    for x in container_statuses:
        if not container_statuses[x].isOk():
            all_ok = False
            break
    if all_ok:
        overall_status = html.Div(className='statusbubble_big', style={'color': 'rgba(114,228,125,1)'})
    else:
        overall_status = html.Div(className='status_bubble_big', style={'color': 'rgba(239,102,102,1)'})
    return html.Ul(
        className='status_group',
        id='container_statuses',
        children=[
            html.Li([
                html.Div('status', className='statustext'),
                overall_status
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

def getStatusDiv(status):
    class_name = 'statusbubble'
    
    # make this thread safe pls
    if status.isOk():
        html.Div(className=class_name, style={'color': 'rgba(114,228,125,1)'})
    else:
        return html.Div(className=class_name, style={'color': 'rgba(239,102,102,1)'})


# TODO: make this display past positions
# TODO: sort positions by amnt of time held?
def getPortfolioPositions(positions):
    elements = []
    for coin in positions:
        if positions[coin]:
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
    if cur_position:
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