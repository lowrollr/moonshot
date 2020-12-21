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
from plotly.subplots import make_subplots
from plotly.offline import plot
from numpy import mean
from dominate.tags import *
from dominate.util import raw
import chart_studio.tools as tls
import os


ALT_AXIS_COLS = {'macd_diff'}

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
    


'''
    ARGS:
        -> dataframe (Dataframe): contains a dataset for a base/quote currency pair, as well as any indicators applied to the data
        -> entries ([[int, float]]): time, close pairs for each occurance when a strategy entered a position
        -> exits ([[int, float]]): time, close pairs for each occurance when a strategy exited a position
        -> indicators_to_graph [string]: list of indicator names to plot
        -> name (string): base file name containing information about the currency pair and strategy being used
        -> padding (int): how much to pad each individual movememnt by (in minutes)
    RETURN:
        -> (((string, {string: value}), {string: value})): tuple containing a tuple with a list of strings corresponding to divs to be inserted into the overall report
            as well as a dictionary containing metrics on the inidividual entry/exit movement, as well as a dictionary containing metrics about the 
            performance of the strategy on the dataset as a whole
    WHAT: 
        -> generates a div element containing an embedded plotly object, as well as generates statistics for individual movements and overall performance
        -> each embedded plotly object contains the candlesticks for the given timeframe as well as the entry/exit pair
        -> will also contain any indicators specified
        -> each timeframe encapsulates the entry/exit point and an additional time periof of padding on each side
        -> talk to Jacob if you don't understand this, there is a lot going on here
    TODO:
        -> its possible some of this could be abstracted
'''
def generate_movement_graphs(dataframe, entries, exits, indicators_to_graph, name, padding=20):
    if not entries:
        return None
    # contains plot div strings to embed
    plots = []

    # holds overall statistics
    overall_stats = {}

    # list of profits compiled through appending all profits from each individual movement
    overall_profits = []

    # list of hold times compiled through appending all hold times from each individual movement
    overall_hold_times = []

    # consider each entry exit pair (their lengths are identical)
    for i, x in enumerate(entries):
        # holds stats for the individual movement
        movement_stats = {}

        # get the entry time and price, and use the entry time to calculate the start of the timeframe to be plotted
        time_entry = x[0]
        price_entry = x[1]
        starting_time = time_entry - (padding * 60)

        # plot the entry point
        ent_graph = go.Scatter(x=[time_entry], y=[price_entry], name='Entry', mode='markers', marker_color='aqua')
        
        # make sure we aren't considering an entry point without a corresponding exit point
        if i < len(exits):
            # get the exit time and price, and use the exit time to calculate the end of the timeframe to be plotted
            time_exit = exits[i][0]
            price_exit = exits[i][1]
            ending_time = time_exit + (padding * 60)

            # plot the exit point
            exit_graph = go.Scatter(x=[time_exit], y=[price_exit], name='Exit', mode='markers', marker_color='purple')
        
            # filter the dataframe to only include data from our specified timeframe
            cur_dataframe = dataframe[(dataframe.time >= starting_time) & (dataframe.time <= ending_time)]

            # generate a candlestick for the data
            candle = go.Candlestick(x=cur_dataframe['time'], open=cur_dataframe['open'], close=cur_dataframe['close'], high=cur_dataframe['high'], low=cur_dataframe['low'], name='Candlesticks')

            # if we are plotting entries/exits, add the appropriate scatter plots to the graph
            inds = []
            secondary_inds = []
            for ind in indicators_to_graph:
                if ind in cur_dataframe.columns: 
                    # give the indicator a random color
                    rand_color = 'rgba(' + str(random.randint(0, 255)) + ', ' + str(random.randint(0, 255)) + ', ' + str(random.randint(0, 255)) + ', 50)'
                    if ind in ALT_AXIS_COLS:
                        secondary_inds.append(go.Scatter(x=cur_dataframe['time'], y=cur_dataframe[ind], name=ind, line=dict(color=(rand_color))))
                    else:
                        inds.append(go.Scatter(x=cur_dataframe['time'], y=cur_dataframe[ind], name=ind, line=dict(color=(rand_color))))

            # bundle all of our plots together into a single object
            # data = candle + inds + ent_graph + exit_graph

            # initialize the plot and save it to a div formatted string that we can embed
            
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            fig.update_layout(title_text='Movement ' + str(i))
            fig.add_trace(candle, secondary_y=False)
            if inds:
                for ind in inds:
                    fig.add_trace(ind, secondary_y=False)
            if secondary_inds:
                for ind in secondary_inds:
                    fig.add_trace(ind, secondary_y=True)
                
            fig.add_trace(ent_graph, secondary_y=False)
            fig.add_trace(exit_graph, secondary_y=False)
            plot_as_div = plot(fig, include_plotlyjs=False, output_type='div')  

            # calculate hold time and percent profit for the movement
            hold_time = (time_exit - time_entry) / 60
            profit = (price_exit - price_entry)
            movement_stats['Hold Time'] = str(int(hold_time)) + ' min'
            movement_stats['% Profit'] = str(round(((price_exit / price_entry) * 100) - 100, 2)) + '%'

            # append the hold time and profit to the overall set of hold times and profits
            overall_hold_times.append(hold_time)
            overall_profits.append(profit)

            # append a tuple containing the stringified plot and movement stats
            plots.append((plot_as_div, movement_stats))

    # calculate metrics for the overall performance
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

'''
    ARGS:
        -> plot_div (string): stringified div object to embed in the html doc
        -> plot_stats ({string: value}): a dictionary containing metrics for the movement
        -> name (string): base file name containing information about the currency pair and strategy being used
        -> movement_num (int): which movement id to number this as
    RETURN:
        -> filename (string): the filename the report was saved at (so we can make a link to it on another page)
    WHAT: 
        -> generates a webpage report for an individual movement and saves it to a file
'''
def generate_movement_page(plot_div, plot_stats, name, movement_num):
    # initialize the HTML document object
    doc = dominate.document(title='Movement ' + str(movement_num))

    # link to stylesheets and plotly script (IMPORTANT)
    with doc.head:
        link(rel='stylesheet', href='./reports/style.css')
        script(type='text/javascript', src='script.js')
        script(src='https://cdn.plot.ly/plotly-latest.min.js')

    
    with doc:
        with div():
            attr(cls='body')
            # embed the plot
            td(raw(plot_div))

            # create a table with statistics about the movement
            with table().add(tbody()):
                for stat in plot_stats:
                    row = tr()
                    row.add(td(stat))
                    row.add(td(plot_stats[stat]))

    # save the file
    filename = name + '_' + 'movement' + str(movement_num) + '.html'
    with open('./reports/' + filename, 'w') as output:
        output.write(str(doc))

    return filename


'''
    ARGS:
        -> dataframe (Dataframe): contains a dataset for a base/quote currency pair, as well as any indicators applied to the data
        -> entries ([[int, float]]): time, close pairs for each occurance when a strategy entered a position
        -> exits ([[int, float]]): time, close pairs for each occurance when a strategy exited a position
        -> indicators_to_graph [string]: list of indicator names to plot
        -> name (string): base file name containing information about the currency pair and strategy being used
        -> report_format (string): specifies how to format the report (links to plots or all plots on one page)
    RETURN:
        -> None
    WHAT: 
        -> generates a webpage report for the strategy execution
'''
def write_report(dataframe, entries, exits, indicators_to_graph, name, report_format):
    # initialize the HTML document object
    doc = dominate.document(title='Overall Report')

    # generate the graphs/stats for individual movements
    movement_plots, overall_stats = generate_movement_graphs(dataframe, entries, exits, indicators_to_graph, name)

    # if the report format is auto, set the format to the appropriate type given the number of plots
    if report_format == 'auto':
        if len(movement_plots) < 20:
            report_format == 'divs'
        else:
            report_format = 'pages'
    filenames = []
    # if the report format is pages, create a page for each entry/exit pair
    if report_format == 'pages':
        
        movement_num = 0
        for mp, mp_stats in movement_plots:
            filenames.append(generate_movement_page(mp, mp_stats, name, movement_num))
            movement_num += 1 

    # link to stylesheets and plotly script (IMPORTANT) 
    with doc.head:
        link(rel='stylesheet', href='./reports/style.css')
        script(type='text/javascript', src='script.js')
        script(src='https://cdn.plot.ly/plotly-latest.min.js')

    with doc:
        with div():
            attr(cls='body')
            # if the report format is div, embed all plots into the single page
            if report_format == 'divs':
                for mp, mp_stats in movement_plots:
                    td(raw(mp))
                    with table().add(tbody()):
                        
                        for stat in mp_stats:
                            row = tr()
                            row.add(td(stat))
                            row.add(td(mp_stats[stat]))
            # if the report format is pages, create links to each other report's page
            elif report_format == 'pages':
                reports_dir = './reports/'
                report_list = ul()
                for i,f in enumerate(filenames):
                    report_list += li(a('Movement #' + str(i), href=reports_dir + f), __pretty=False)

            else:
                raise Exception('Invalid report format!')
            
    # write the report to a file
    with open('./reports/' + name + '_overall_report.html', 'w') as output:
        output.write(str(doc))

