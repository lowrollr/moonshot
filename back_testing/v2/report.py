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
from alive_progress import alive_bar
import chart_studio.tools as tls
import os
from v2.utils import getRandomSpinner


ALT_AXIS_COLS = {'macd_diff', "PSAR", "RateOfChange", "RateOfChange_shorter"}


'''
    ARGS:
        -> dataframe (Dataframe): contains a dataset for a base/quote currency pair, as well as any indicators applied to the data
        -> entries ([[int, float]]): time, close pairs for each occurance when a strategy entered a position
        -> exits ([[int, float]]): time, close pairs for each occurance when a strategy exited a position
        -> indicators_to_graph [string]: list of indicator names to plot
        -> name (string): base file name containing information about the currency pair and strategy being used
        -> fees (float): fees we pay on each transaction (passed from config)
        -> padding (int): how much to pad each individual movememnt by (in minutes)
    RETURN:
        -> (((string, {string: value}), {string: value})): tuple containing a tuple with a list of strings corresponding to divs to be inserted into the overall report
            as well as a dictionary containing metrics on the inidividual entry/exit movement, as well as a dictionary containing metrics about the 
            performance of the strategy on the dataset as a whole
    WHAT: 
        -> generates a div element containing an embedded plotly object, as well as generates statistics for individual movements and overall performance
        -> each embedded plotly object contains the candlesticks for the given timeframe as well as the entry/exit pair
        -> will also contain any indicators specified
        -> each timeframe encapsulates the entry/exit point and an additional time period of padding on each side
        -> talk to Jacob if you don't understand this, there is a lot going on here
    TODO:
        -> its possible some of this could be abstracted
'''
def generate_movement_graphs(dataframe, entries, exits, indicators_to_graph, name, fees, padding=60):
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
    with alive_bar(len(exits), spinner=getRandomSpinner()) as bar:
        # consider each entry exit pair (their lengths are identical)
        for i, x in enumerate(entries):
            # holds stats for the individual movement
            movement_stats = {}

            # get the entry time and price, and use the entry time to calculate the start of the timeframe to be plotted
            time_entry = x[0]
            price_entry = x[1]
            starting_time = time_entry - (padding * 60000)

            # plot the entry point
            ent_graph = go.Scatter(x=[time_entry], y=[price_entry], name='Entry', mode='markers', marker_color='aqua')
            
            # make sure we aren't considering an entry point without a corresponding exit point
            if i < len(exits):
                # get the exit time and price, and use the exit time to calculate the end of the timeframe to be plotted
                time_exit = exits[i][0]
                price_exit = exits[i][1]
                ending_time = time_exit + (padding * 60000)

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
                fig.update_layout(template='plotly_dark', title_text='Movement ' + str(i))
                fig.add_trace(candle, secondary_y=False)
                if inds:
                    for ind in inds:
                        fig.add_trace(ind, secondary_y=False)
                # add any secondary indicators to their own axis
                if secondary_inds:
                    for ind in secondary_inds:
                        fig.add_trace(ind, secondary_y=True)
                    
                fig.add_trace(ent_graph, secondary_y=False)
                fig.add_trace(exit_graph, secondary_y=False)
                plot_as_div = plot(fig, include_plotlyjs=False, output_type='div')  

                # calculate hold time and percent profit for the movement
                hold_time = (time_exit - time_entry) / 60000
                profit = round(((price_exit / price_entry) * 100) - 100, 2)
                movement_stats['Hold Time'] = str(int(hold_time)) + ' min'
                movement_stats['% Profit'] = str(profit) + '%'

                # append the hold time and profit to the overall set of hold times and profits
                overall_hold_times.append(hold_time)
                overall_profits.append(profit)

                # append a tuple containing the stringified plot and movement stats
                plots.append((plot_as_div, movement_stats))
                bar()

    profit_arr = [x for x in overall_profits if x > 0]
    loss_arr = [x for x in overall_profits if x < 0]

    profitable_trades = []
                #   time,       fee
    fee_changes = [(fees[0][2], fees[0][1])]

    for fee in fees:
        if fee[1] != fee_changes[-1][1]:
            fee_changes.append((fee[2], fee[1]))

    for i in range(len(overall_profits)):
        fee = 0.5
        for time_fee in fee_changes:
            if overall_hold_times[i] > time_fee[0]:
                fee = time_fee[1]
        if overall_profits[i] > fee:
            profitable_trades.append(1)
        else:
            profitable_trades.append(0)

    # calculate metrics for the overall performance
    overall_stats['Total Trades'] = len(overall_hold_times)
    overall_stats['Average Hold Time'] = str(round(mean(overall_hold_times), 2)) + ' min'
    overall_stats['Maximum Hold Time'] = str(round(max(overall_hold_times), 2)) + ' min'
    overall_stats['Minimum Hold Time'] = str(round(min(overall_hold_times), 2)) + ' min'
    overall_stats['Average Profit (%)'] = str(round(mean(overall_profits), 2)) + '%'
    overall_stats['Profit Average (%)'] = round(mean(profit_arr), 2)
    overall_stats['Loss Average (%)'] = round(mean(loss_arr), 2)
    overall_stats['Max Profit (%)'] = str(round(max(overall_profits), 2)) + '%'
    overall_stats['Max Drawdown (%)'] = str(round(min(overall_profits), 2)) + '%'
    overall_stats['Percentage of Trades Profitable'] = round(sum(profitable_trades) / len(profitable_trades) * 100, 2)
    
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
        link(rel='stylesheet', href='style.css')
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
        -> other_stats ({string: value}): specifies other stats about the strategy exection to display
        -> fees (float): fees we pay on each transaction (passed from config)
    RETURN:
        -> None
    WHAT: 
        -> generates a webpage report for the strategy execution
'''
def write_report(dataframe, entries, exits, indicators_to_graph, name, report_format, other_stats, fees):
    # initialize the HTML document object
    doc = dominate.document(title='Overall Report')

    # generate the graphs/stats for individual movements
    movement_plots, overall_stats = generate_movement_graphs(dataframe, entries, exits, indicators_to_graph, name, fees)

    # if the report format is auto, set the format to the appropriate type given the number of plots
    if report_format == 'auto':
        if len(movement_plots) < 20:
            report_format = 'divs'
        else:
            report_format = 'pages'
    filenames = []
    # if the report format is pages, create a page for each entry/exit pair
    if report_format == 'pages':
        
        movement_num = 0
        for mp, mp_stats in movement_plots:
            filenames.append(generate_movement_page(mp, mp_stats, name, movement_num))
            movement_num += 1 

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(go.Scatter(x=dataframe['time'], y=dataframe['account_value'], name='account_value'), secondary_y=False)
    fig.add_trace(go.Scatter(x=dataframe['time'], y=dataframe['close'], name='asset value'), secondary_y=True)
    fig.update_layout(template='plotly_dark', title='Overall Profit Growth vs. Asset Growth')
    overall_as_div = plot(fig, include_plotlyjs=False, output_type='div')  

    # link to stylesheets and plotly script (IMPORTANT) 
    with doc.head:
        link(rel='stylesheet', href='style.css')
        script(type='text/javascript', src='script.js')
        script(src='https://cdn.plot.ly/plotly-latest.min.js')

    with doc:
        with div():
            # add the overall performance graph to the page
            td(raw(overall_as_div))
            attr(cls='body')
            # create and populate the overall stats table
            h1('Overall Stats')
            with table().add(tbody()):
                for stat in overall_stats:
                    row = tr()
                    row.add(td(stat))
                    row.add(td(overall_stats[stat]))
                for stat in other_stats:
                    row = tr()
                    row.add(td(stat))
                    row.add(td(other_stats[stat]))

            h1('Individual Movements')
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
                report_list = ul()
                
                with table(id="ind_movements_data").add(tbody()):
                    stat_types = list(movement_plots[0][1].keys())
                    row = tr()
                    row.add(td('Movement'))
                    for i in range (len(stat_types)):
                        row.add(th(stat_types[i], onclick="sortRows(" + str(i+1) + ")"))
                    for i,f in enumerate(filenames):
                        mp_stats = movement_plots[i][1]
                        new_row = tr()
                        new_row.add(td(a('Movement #' + str(i), href=f, target='_blank'), __pretty=False))
                        for stat in stat_types:
                            new_row.add(td(mp_stats[stat]))
            else:
                raise Exception('Invalid report format!')
            
    # write the report to a file
    with open('./reports/' + name + '_overall_report.html', 'w') as output:
        output.write(str(doc))

# def multiProcessCoinDataGen(name, dataset, entries, exits, indicators_to_graph, fees):
#     coin_stats = dict()
#     filename = []
#     temp_coin_plots = dict()
#     coin_movement_plots = []
#     graphs = generate_movement_graphs(dataset, entries, exits, indicators_to_graph, name, fees)
#     if graphs:
#         coin_movement_plots, coin_stats = graphs
#         movement_num = 0
#         for mp, mp_stats in coin_movement_plots:
#             filename.append()

def writePMReport(coin_datasets, entries, exits, portfolio_growth, portfolio_allocation, coin_weights, indicators_to_graph, fees, buy_signals, sell_signals, volume_bars):
    doc = dominate.document(title='Portfolio Manager Report')

    coin_stats = dict()
    filenames = dict()
    coin_plots = dict()
    coin_movement_plots = dict()
    for name, dataset in coin_datasets:
        #change
        graphs = generate_movement_graphs(dataset, entries[name], exits[name], indicators_to_graph, name, fees)
        if graphs:
            coin_movement_plots[name], coin_stats[name] = graphs
            movement_num = 0
            filenames[name] = []
            for mp, mp_stats in coin_movement_plots[name]:
                filenames[name].append(generate_movement_page(mp, mp_stats, name, movement_num))
                movement_num += 1
            
            coin_stats[name]["Asset RateOfChange (%)"] = round(((dataset['close'].iloc[-1] - dataset['close'].iloc[0]) / dataset['close'].iloc[0]), 3) * 100
            # coin_stats[name]["Profit Average(%)"]
            fig = make_subplots()
            fig.update_layout(template='plotly_dark', title_text=f'{name}')
            fig.add_trace(go.Scatter(x=dataset['time'], y=dataset['close'], name='Close Price'))
            fig.add_trace(go.Scatter(x=[a[0] for a in entries[name]], y=[a[1] for a in entries[name]], name='Entry', mode='markers', marker_color='aqua'))
            fig.add_trace(go.Scatter(x=[a[0] for a in exits[name]], y=[a[1] for a in exits[name]], name='Exit', mode='markers', marker_color='purple'))
            
            coin_plots[name] = plot(fig, include_plotlyjs=False, output_type='div')
    
    time_amount = volume_bars[-1][0] - volume_bars[0][0]
    num_bars = len(volume_bars)

    bar_width = int(0.9 * (time_amount / num_bars))

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.update_layout(template='plotly_dark', title_text='Portfolio Growth')
    times = [x[0] for x in portfolio_growth]
    port_values = [x[1] for x in portfolio_growth]
    fig.add_trace(go.Scatter(x=times, y=port_values, name='Portfolito Value'), secondary_y=False)
    fig.add_trace(go.Bar(x=[a[0] for a in volume_bars], y=[a[1] for a in volume_bars], name='Total Trade Volume', opacity=0.25, marker_color='grey', width=bar_width), secondary_y=True)
    growth_plot = plot(fig, include_plotlyjs=False, output_type='div')

    fig = make_subplots()
    
    for coin in portfolio_allocation:
        times = [x[0] for x in portfolio_allocation[coin]]
        values = [x[1] for x in portfolio_allocation[coin]]
        fig.add_trace(go.Scatter(x=times, y=values, name=coin))
    fig.update_layout(template='plotly_dark', title_text='Portfolio Allocation')
    allocation_plot = plot(fig, include_plotlyjs=False, output_type='div')

    fig = make_subplots()
    
    for coin in coin_weights:
        times = [x[0] for x in coin_weights[coin]]
        weights = [x[1] for x in coin_weights[coin]]
        fig.add_trace(go.Scatter(x=times, y=weights, name=coin))
    fig.update_layout(template='plotly_dark', title_text='Coin Weights')
    weights_plot = plot(fig, include_plotlyjs=False, output_type='div')

    #fees
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.update_layout(template='plotly_dark', title_text='30-day Volume + Fees')
    times = [x[2] for x in fees]
    fee_vals = [x[1] for x in fees]
    volume_vals = [x[0] for x in fees]
    fig.add_trace(go.Scatter(x=times, y=fee_vals, name='Fee Values'), secondary_y=False)
    fig.add_trace(go.Scatter(x=times, y=volume_vals, name='30-day Volume Values'), secondary_y=True)
    
    fees_plot = plot(fig, include_plotlyjs=False, output_type='div')

    with doc.head:
        link(rel='stylesheet', href='style.css')
        script(type='text/javascript', src='script.js')
        script(src='https://cdn.plot.ly/plotly-latest.min.js')

    avg_asset_roc = round((sum([coin_stats[x]["Asset RateOfChange (%)"] for x in coin_stats])/len(coin_stats)), 1)
    # profit_avg = round((sum([coin_stats[x]["Average Profit(%)"] for x in coin_stats if coin_stats[x]["Average Profit(%)"] > 0])))
    # loss_avg = round((sum([coin_stats[x]["Average Profit(%)"] for x in coin_stats if coin_stats[x]["Average Profit(%)"] < 0])))
    portfolio_roc = round((port_values[-1]*100 - port_values[0]*100)/(port_values[0]), 1)
    total_trades =  int(sum([coin_stats[x]["Total Trades"] for x in coin_stats]))
    #
    avg_profit_avg = round(sum([float(coin_stats[x]['Percentage of Trades Profitable'])/100 * float(coin_stats[x]["Total Trades"]) * float(coin_stats[x]["Profit Average (%)"]) for x in coin_stats])/
    sum([float(coin_stats[x]['Percentage of Trades Profitable'])/100 * int(coin_stats[x]['Total Trades']) for x in coin_stats]), 2)
    avg_loss_avg = round(sum([float(1 - coin_stats[x]['Percentage of Trades Profitable'])/100 * float(coin_stats[x]["Total Trades"]) * float(coin_stats[x]["Loss Average (%)"]) for x in coin_stats])/
    sum([float(1 - coin_stats[x]['Percentage of Trades Profitable'])/100 * int(coin_stats[x]['Total Trades']) for x in coin_stats]), 2)

    tot_win = round((sum([float(coin_stats[x]['Percentage of Trades Profitable'])/100 * float(coin_stats[x]["Total Trades"]) for x in coin_stats])/sum([int(coin_stats[x]['Total Trades']) for x in coin_stats]) * 100), 2)

    with doc:
        with div():
            attr(cls='body')
            h1('Overall Stats')
            td(raw(growth_plot))
            with table().add(tbody()):
                tr().add(td("Initial Portfolio Value :")).add(td(round(port_values[0], 2)))
                tr().add(td("Exit Portfolio value: ")).add(td(round(port_values[-1], 2)))
                tr().add(td("Portfolio RateOfChange (%)")).add(td(str(portfolio_roc) + "%"))
                tr().add(td("Asset Avg. RateOfChange (%)")).add(td(str(avg_asset_roc) + "%"))
                tr().add(td("Total Trades: ")).add(td(str(total_trades)))
                tr().add(td("Total Average of Average Profit: ")).add(td(str(avg_profit_avg) + "%"))
                tr().add(td("Total Average of Average Loss: ")).add(td(str(avg_loss_avg) + "%"))
                tr().add(td("Overall Win Rate: ")).add(td(str(tot_win) + "%"))

            td(raw(allocation_plot))
            td(raw(weights_plot))
            td(raw(fees_plot))
            any_coin = list(coin_plots.keys())[0]
            stat_types = list(coin_movement_plots[any_coin][0][1].keys())
            for coin_num, coin in enumerate(coin_plots):
                coin_plot = coin_plots[coin] 
                h1(f'{coin} Stats')
                td(raw(coin_plot))
                with table().add(tbody()):
                    for stat in coin_stats[coin]:
                        row = tr()
                        row.add(td(stat))
                        if stat == "Percentage of Trades Profitable" or stat == "Asset RateOfChange (%)" or stat == "Profit Average (%)" or stat == "Loss Average (%)":
                            row.add(td(str(round(coin_stats[coin][stat], 2)) + "%"))
                        else:
                            row.add(td(coin_stats[coin][stat]))
                h1(f'{coin} Movements', onclick=f"revealTable({coin_num})")
                report_list = ul()

                with table(style="display: none", id=f"ind_movements_data{coin_num}").add(tbody()):
                    attr(cls="table_movements")
                    row = tr()
                    row.add(td('Movement'))
                    for i in range (len(stat_types)):
                        row.add(th(stat_types[i], onclick=f"sortRows({str(i+1)}, {coin_num})"))
                    for i,f in enumerate(filenames[coin]):
                        mp_stats = coin_movement_plots[coin][i][1]
                        new_row = tr()
                        new_row.add(td(a('Movement #' + str(i), href=f, target='_blank'), __pretty=False))
                        for stat in stat_types:
                            new_row.add(td(mp_stats[stat]))
        # write the report to a file
    with open('./reports/PM_overall_report.html', 'w') as output:
        output.write(str(doc))