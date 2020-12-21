'''
FILE: model.py
AUTHORS:
    -> Jacob Marshall (marshingjay@gmail.com)
WHAT:
    -> This file contains all functionality associates with generating HTML report pages
'''

import dominate
import random
import plotly.graph_objs as go
from plotly.offline import plot
from numpy import mean
from dominate.tags import *
from dominate.util import raw
import chart_studio.tools as tls
import os


'''
    ARGS:
        -> dataset (Dataframe): contains a dataset for a base/quote currency pair, as well as any indicators applied to the data
        -> entries ([[int, float]]): time, close pairs for each occurance when a strategy entered a position
        -> exits ([[int, float]]): time, close pairs for each occurance when a strategy exited a position
        -> indicators_to_graph [string]: list of indicator names to plot
        -> name (string): base file name containing information about the currency pair and strategy being used
        -> stop_loss_plot: (go.Scatter): plot of stop loss from a strategy that can optionally be added to the graph
    RETURN:
        -> None
    WHAT: 
        -> plots a candlestick graph for the execution of a given strategy on a dataset
        -> plots entry and exit points, as well as OHCL data for each minute
        -> outputs the graph to a file, constructed with name
    TODO:
        -> figure out whether or not this is still useful (as opposed to the segmented report)
'''
def generate_overall_graph(dataset, entries, exits, indicators_to_graph, name, stop_loss_plot=None):
    # create a candlestick object for the data in the dataset
    candle = go.Candlestick(x=dataset['time'], open=dataset['open'], close=dataset['close'], high=dataset['high'], low=dataset['low'], name='Candlesticks')
    inds = []
    data=[]
    # create scatter plots for each indicator passed
    for x in indicators_to_graph:
        if x in dataset.columns: 
            # give the indicator a random color
            rand_color = 'rgba(' + str(random.randint(0, 255)) + ', ' + str(random.randint(0, 255)) + ', ' + str(random.randint(0, 255)) + ', 50)'
            inds.append(go.Scatter(x=dataset['time'], y=dataset[x], name=x, line=dict(color=(rand_color))))

    # if we are plotting entries/exits, add the appropriate scatter plots to the graph
    if entries: 
        ent_graph = go.Scatter(x=[item[0] for item in entries], y=[item[1] for item in entries], name='Entries', mode='markers')
        exit_graph = go.Scatter(x=[item[0] for item in exits], y=[item[1] for item in exits], name='Exits', mode='markers')
        # concatenate all our plots into a single list to be displayed
        data = [candle] + inds + [ent_graph, exit_graph]
    else:
        # concatenate all our plots into a single list to be displayed
        data = [candle] + inds

    # if we have recieved a stop loss plot, add that to the plot as well
    if stop_loss_plot:
        data.append([stop_loss_plot])

    # initialize the plot and plot the data, save to <name>.html
    layout = go.Layout(title=name)
    fig = go.Figure(data=data, layout=layout)
    plot(fig, filename='plots/' + name + '.html')
    



def generate_movement_graphs(dataframe, entries, exits, indicators_to_graph, name, padding=20):
    plots = []
    overall_stats = {}
    overall_profits = []
    overall_hold_times = []
    for i, x in enumerate(entries):
        movement_stats = {}
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
            hold_time = (time_exit - time_entry) / 60
            profit = (price_exit - price_entry)
            movement_stats['Hold Time'] = str(int(hold_time)) + ' min'
            movement_stats['% Profit'] = str(round(((price_exit / price_entry) * 100) - 100, 2)) + '%'
            overall_hold_times.append(hold_time)
            overall_profits.append(profit)

            plots.append((plot_as_div, movement_stats))
    overall_stats['entry_exit_pairs'] = len(overall_hold_times)
    overall_stats['avg_hold_time'] = mean(overall_hold_times)
    overall_stats['max_hold_time'] = max(overall_hold_times)
    overall_stats['min_hold_time'] = min(overall_hold_times)
    overall_stats['avg_profit'] = mean(overall_profits)
    overall_stats['max_profit'] = max(overall_profits)
    overall_stats['min_profit'] = min(overall_profits)
    overall_stats['percent_profitable'] = sum([x > 0 for x in overall_profits]) / len(overall_profits)
    overall_stats['total_profit'] = sum(overall_profits)
    overall_stats['pervent_profit'] = ((1000000 + overall_stats['total_profit']) / 1000000) * 100
    return (plots, overall_stats)


def generate_movement_page(plot_div, plot_stats, name, movement_num):
    doc = dominate.document(title='Movement ' + str(movement_num))
    with doc.head:
        link(rel='stylesheet', href='./reports/style.css')
        script(type='text/javascript', src='script.js')
        script(src='https://cdn.plot.ly/plotly-latest.min.js')
    with doc:
        with div():
            attr(cls='body')
            td(raw(plot_div))
            with table().add(tbody()):
                for stat in plot_stats:
                    row = tr()
                    row.add(td(stat))
                    row.add(td(plot_stats[stat]))
    filename = name + '_' + 'movement' + str(movement_num) + '.html'
    with open('./reports/' + filename, 'w') as output:
        output.write(str(doc))
    return filename

def write_report(dataframe, entries, exits, indicators_to_graph, name, report_format):
    # movement_graphs = generate_movement_graphs(dataset, entries, exits)
    doc = dominate.document(title='Overall Report')
    movement_plots, overall_stats = generate_movement_graphs(dataframe, entries, exits, indicators_to_graph, name)

    if report_format == 'auto':
        if len(movement_plots) < 20:
            report_format == 'divs'
        else:
            report_format = 'pages'
    filenames = []
    if report_format == 'pages':
        
        movement_num = 0
        for mp, mp_stats in movement_plots:
            filenames.append(generate_movement_page(mp, mp_stats, name, movement_num))
            
            movement_num += 1 


    with doc.head:
        link(rel='stylesheet', href='./reports/style.css')
        script(type='text/javascript', src='script.js')
        script(src='https://cdn.plot.ly/plotly-latest.min.js')

    with doc:
        with div():
            attr(cls='body')
            
            if report_format == 'divs':
                for mp, mp_stats in movement_plots:
                    td(raw(mp))
                    with table().add(tbody()):
                        
                        for stat in mp_stats:
                            row = tr()
                            row.add(td(stat))
                            row.add(td(mp_stats[stat]))
            elif report_format == 'pages':
                reports_dir = './reports/'
                report_list = ul()
                for i,f in enumerate(filenames):
                    report_list += li(a('Movement #' + str(i), href=reports_dir + f), __pretty=False)

            
            else:
                raise Exception('Invalid report format!')
            
            
    with open('test_output.html', 'w') as output:
        output.write(str(doc))

