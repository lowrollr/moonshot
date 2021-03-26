import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from plotly.subplots import make_subplots


def createPage(toptext, plot, position_elems, status_elems, coins, cur_coin):
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
            children=createPageContent(toptext, plot, position_elems, status_elems, coins, cur_coin))
    ])
        

def createPageContent(toptext, plot, position_elems, status_elems, coins, cur_coin):
    return [
        
        html.Div(className='background'),
        html.Div(
            className='sidebar',
            children=[
                getDropdown(coins, cur_coin),
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
                    className='asset_plot',
                    figure=plot,
                    config={'showTips': False, 
                            'displaylogo': False,
                            'watermark': False,
                            'staticPlot': True,}
                    )
            ]
        )
    ]

def getTopText(data, asset):
    
    cur_value = '$0.00'
    delta = '+$0.00'
    perc_change = '+0.00%'
    if data:
        cur_value = data[-1][0]
        first_value = data[0][0]
        if asset == 'PORTFOLIO':
            cur_value = round(cur_value, 2)
            first_value = round(first_value, 2)
        delta = cur_value - first_value
        perc_change = ((cur_value - first_value) / first_value) * 100
        split_first = str(first_value).split('.')
        split_cur = str(cur_value).split('.')
        precision = 2
        if len(split_first) == 2:
            if len(split_cur) == 2:
                precision = max(len(split_first[1]), len(split_cur[1]))
            else:
                precision = len(split_first[1])
        delta = round(delta, precision)
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

def getDropdown(coins, cur_coin):
    options = [{'label': 'PORTFOLIO', 'value': 'PORTFOLIO'}]
    for x in coins:
        options.append({'label': x, 'value': x})
    return dcc.Dropdown(id='dropdown', options=options, value=cur_coin)

#TODO: plot volume on secondary axis
#TODO: add timestamps to x axis & data points
def getFig(datastream, positions=None):
    fig = make_subplots()
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False,
            xaxis=dict(
                showgrid=False,  # Removes X-axis grid lines
                zeroline=False,
                showline=False,
                tickfont = dict(
                    family = 'Space Mono',
                    size = 20,
                    color = '#ebf5ff'
                ),
            ),
            yaxis=dict(
                showgrid=False,  # Removes Y-axis grid lines
                zeroline=False,    
                showline=False,
                tickfont = dict(
                    family = 'Space Mono',
                    size = 20,
                    color = '#ebf5ff'
                ),
            )
            )

    
    if datastream:
        values, _, indices = zip(*list(datastream))
        going_up = values[0] <= values[-1]
        linecolor = 'rgba(239,102,102,1)'
        if going_up:
            linecolor = 'rgba(114,228,126,1)'
        fig.add_trace(go.Scatter(x=indices, y=values, line=dict(color=linecolor)) )
    if positions:
        enter_indices = []
        enter_values = []
        partial_indices = []
        partial_values = []
        exit_indices = []
        exit_values = []
        for x in positions:
            if x['type'] == 'enter':
                enter_indices.append(x['datetime'])
                enter_values.append(x['value'])
            elif x['type'] == 'exit':
                exit_indices.append(x['datetime'])
                exit_values.append(x['value'])
            else:
                partial_indices.append(x['datetime'])
                partial_values.append(x['value'])
        fig.add_trace(go.Scatter(x=enter_indices, y=enter_values, mode="markers", marker_color="green", marker_size=13, marker_symbol="arrow-bar-right"))
        fig.add_trace(go.Scatter(x=exit_indices, y=exit_values, mode="markers", marker_color="red", marker_size=13, marker_symbol="arrow-bar-left"))
        fig.add_trace(go.Scatter(x=partial_indices, y=partial_values, mode="markers", marker_color="yellow", marker_size=13, marker_symbol="arrow-left"))
    return fig




def getStatusElems(container_statuses):
    all_ok = True
    for x in container_statuses:
        if not container_statuses[x].isOk():
            all_ok = False
            break
    if all_ok:
        overall_status = html.Div(className='statusbubble_big', style={'background': 'rgba(114,228,125,1)'})
    else:
        overall_status = html.Div(className='statusbubble_big', style={'background': 'rgba(239,102,102,1)'})
    return html.Ul(
        className='status_group',
        id='container_statuses',
        children=[
            html.Li([
                html.Div('status', className='overall_statustext'),
                overall_status
            ], className = 'statuspair'),
            html.Li([
                html.Div('Data Consumer', className='statustext'),
                getStatusDiv(container_statuses['Data Consumer'])
            ], className = 'statuspair'),
            html.Li([
                html.Div('Portfolio Manager', className='statustext'),
                getStatusDiv(container_statuses['Portfolio Manager'])
            ], className = 'statuspair'),
            html.Li([
                html.Div('Compute Engine', className='statustext'),
                getStatusDiv(container_statuses['Compute Engine'])
            ], className = 'statuspair'),
            html.Li([
                html.Div('Coinbase', className='statustext'),
                getStatusDiv(container_statuses['Coinbase'])
            ], className = 'statuspair'),
        ]
    )

def getStatusDiv(status):
    class_name = 'statusbubble'
    if status.isOk():
        return html.Div(className=class_name, style={'background': 'rgba(114,228,125,1)'})
    else:
        return html.Div(className=class_name, style={'background': 'rgba(239,102,102,1)'})


# TODO: make this display past positions
# TODO: sort positions by amnt of time held?
def getPortfolioPositions(positions):
    elements = []
    for coin in positions:
        if positions[coin]:
            cur_amnt = round(positions[coin]['amnt'],  4)
            cur_price = positions[coin]['price']
            profit = round(positions[coin]['profit'], 2)
            style = {'background': 'rgba(239,102,102,0.3)'}
            if profit > 0:
                style = {'background': 'rgba(114,228,125,0.3)'}
            if profit > 0:
                profit = '+' + str(profit) + '%'
            else:
                profit = str(profit) + '%'
            alloc = round(positions[coin]['alloc'], 3)
            
            element = html.Li(
                className='position',
                children=[
                    html.Span(className="statCoin", children=coin),
                    html.Span(className="statAmntOwned", children=cur_amnt),
                    html.Span(className="statCurPrice", children=f'${cur_price}'),
                    html.Span(className="statCurProfit", children=profit),
                    html.Span(className="statCurAlloc", children=alloc),
                 ],
                 style=style,
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
        cur_amnt = round(cur_position['amnt'], 4)
        cur_price = cur_position['price']
        profit = round(cur_position['profit'], 2)
        style = {'background': 'rgba(239,102,102,0.3)'}
        if profit > 0:
            style = {'background': 'rgba(114,228,125,0.3)'}
        if profit > 0:
            profit = '+' + str(profit) + '%'
        else:
            profit = str(profit) + '%'

        

        alloc = round(cur_position['alloc'], 3)
        element = html.Li(
                className='position',
                children=[
                    html.Span(className="statCoin", children=coin),
                    html.Span(className="statAmntOwned", children=cur_amnt),
                    html.Span(className="statCurPrice", children=f'${cur_price}'),
                    html.Span(className="statCurProfit", children=profit),
                    html.Span(className="statCurAlloc", children=alloc),
                 ],
                style=style,
            )
        elements.append(element)

    return html.Ul(
        className='position_list',
        children=elements
    )