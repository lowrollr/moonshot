
import dominate
import random
import plotly.graph_objs as go
from plotly.offline import plot
from dominate.tags import *
from dominate.util import raw
import chart_studio.tools as tls
import os


def generate_overall_graph(dataset, entries, exits, indicators_to_graph, name, stop_loss_plot=None):
    candle = go.Candlestick(x=dataset['time'], open=dataset['open'], close=dataset['close'], high=dataset['high'], low=dataset['low'], name='Candlesticks')
    inds = []
    data=[]
    for x in indicators_to_graph:
        if x in dataset.columns: 
            # give the indicator a random color
            rand_color = 'rgba(' + str(random.randint(0, 255)) + ', ' + str(random.randint(0, 255)) + ', ' + str(random.randint(0, 255)) + ', 50)'
            inds.append(go.Scatter(x=dataset['time'], y=dataset[x], name=x, line=dict(color=(rand_color))))
    if entries: # if we are plotting entries/exits, add the appropriate scatter plots to the graph
        ent_graph = go.Scatter(x=[item[0] for item in entries], y=[item[1] for item in entries], name='Entries', mode='markers')
        exit_graph = go.Scatter(x=[item[0] for item in exits], y=[item[1] for item in exits], name='Exits', mode='markers')
        # concatenate all our plots into a single list to be displayed
        data = [candle] + inds + [ent_graph, exit_graph]
    else:
        # concatenate all our plots into a single list to be displayed
        data = [candle] + inds

    if stop_loss_plot:
        data.append([stop_loss_plot])
    layout = go.Layout(title=name)
    fig = go.Figure(data=data, layout=layout)
    # plot(fig, filename='plots/' + name + '.html')
    plot_as_div = plot(fig, include_plotlyjs=False, output_type='div')



def generate_movement_graphs(dataframe, entries, exits, indicators_to_graph, name, padding=20):
    plots = []
    for i, x in enumerate(entries):
        time_entry = x[0]
        price_entry = x[1]
        starting_time = time_entry - (padding * 60)
        ent_graph = [go.Scatter(x=[time_entry], y=[price_entry], name='Entry', mode='markers', marker_color='aqua')]
        exit_graph = []
        ending_time = starting_time
        if i < len(exits):
            time_exit = exits[i][0]
            price_exit = exits[i][1]
            ending_time = time_exit + (padding * 60)
            exit_graph = [go.Scatter(x=[time_exit], y=[price_exit], name='Exit', mode='markers', marker_color='purple')]
        else:
            ending_time = 99999999999999999
        cur_dataframe = dataframe[(dataframe.time >= starting_time) & (dataframe.time <= ending_time)]
        candle = [go.Candlestick(x=cur_dataframe['time'], open=cur_dataframe['open'], close=cur_dataframe['close'], high=cur_dataframe['high'], low=cur_dataframe['low'], name='Candlesticks')]
        inds = []
        for ind in indicators_to_graph:
            if ind in cur_dataframe.columns: 
                # give the indicator a random color
                rand_color = 'rgba(' + str(random.randint(0, 255)) + ', ' + str(random.randint(0, 255)) + ', ' + str(random.randint(0, 255)) + ', 50)'
                inds.append(go.Scatter(x=cur_dataframe['time'], y=cur_dataframe[ind], name=ind, line=dict(color=(rand_color))))
        data = candle + inds + ent_graph + exit_graph
        layout = go.Layout(title='Movement ' + str(i))
        fig = go.Figure(data=data, layout=layout)
        plot_as_div = plot(fig, include_plotlyjs=False, output_type='div')  
        plots.append(plot_as_div)

    return plots

def write_report(dataframe, entries, exits, indicators_to_graph, name):
    # movement_graphs = generate_movement_graphs(dataset, entries, exits)
    doc = dominate.document(title='Test Report')
    movement_plots = generate_movement_graphs(dataframe, entries, exits, indicators_to_graph, name)
    with doc.head:
        link(rel='stylesheet', href='style.css')
        script(type='text/javascript', src='script.js')
        script(src='https://cdn.plot.ly/plotly-latest.min.js')
        

    with doc:
        with div():
            attr(cls='body')
            for mp in movement_plots:
                td(raw(mp))
    with open('test_output.html', 'w') as output:
        output.write(str(doc))

