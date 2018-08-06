import numpy as np
import pandas as pd
import plotly as py
import plotly.graph_objs as go

"""
Author: Rafał Zaręba

Module with calculating and visualization functions
"""


def prepare_data(path, save, save_path):
    """
    Function preparing data downloaded from Dukascopy
    :param path: downloaded file path
    :param save: boolean, if True, prepared data will be saved to save_path location
    :param save_path: if save is True, then pass this as new file path
    :return: prepared data with datetime index and columns: 'Open', 'High', 'Low', 'Close' and 'Volume'
    """
    data = pd.read_csv(path, index_col='Gmt time', dayfirst=True, parse_dates=True)
    data.index.names = ['Date']

    if save:
        data.to_csv(save_path)

    return data


def calculate_ratios(obj, print_ratios=True):
    """
    Function calculating investing ratios
    :param obj: financial strategy instance object
    :param print_ratios: default = True, if True, prints calculated ratios
    :return: tuple of ratios: (market_return, strategy_return, max_drawdown,
    drawdown_period, drawdown_start, drawdown_end)
    """

    # Cumulative Returns
    market_return = obj.data.iloc[-1, obj.data.columns.get_loc('Market Equity')] - 1
    strategy_return = obj.data.iloc[-1, obj.data.columns.get_loc('Strategy Equity')] - 1

    # Calculating investing ratios
    # maximum money drawdown
    df = obj.data['Strategy Equity'].dropna()
    drawdown_end = np.argmax(np.maximum.accumulate(df) - df)
    drawdown_start = np.argmax(df[:drawdown_end])
    drawdown_period = drawdown_end - drawdown_start
    max_drawdown = (df.loc[drawdown_start] - df.loc[drawdown_end]) * 100

    #RAR
    rar = strategy_return*100/max_drawdown

    if print_ratios:
        print('RATIOS:\n\n'
              'Market return: {:1.2f}%\n'              
              'Strategy return: {:1.2f}%\n'
              'Max Drawdown: {:1.2f}%\n'
              'Drawdown period: {}\n'
              'RAR: {:1.2f}'.format(market_return*100, strategy_return*100, -max_drawdown,
                                    drawdown_period, rar))

    ratios = (market_return, strategy_return, max_drawdown,
              drawdown_period, drawdown_start, drawdown_end, rar)

    # Setting instance ratios
    obj.ratios = ratios


def plot_results(obj):
    """
    Function plotting strategy results
    :param data: pandas Data Frame with calculated column Strategy, Strategy Equity
    :param ratios: calculated tuple of ratios from function calculate_ratios
    :return: prints out graph of strategy results
    """
    # Creating daily data for histogram
    daily_data = pd.DataFrame(obj.data['Strategy'])
    daily_data = daily_data.resample('D').sum()
    daily_data['Strategy Equity'] = daily_data['Strategy'].cumsum() + 1

    # Creating columns with weekdays and months
    obj.data['Weekday'] = obj.data.index.weekday
    obj.data['Month'] = obj.data.index.month

    weekdays_list = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    noweekends_list = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

    months_dict = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June', 7: 'July',
                   8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'}
    months_list = list(months_dict.values())

    # Fill the Weekday and Month columns with names
    obj.data['Weekday'] = obj.data['Weekday'].apply(lambda idx: weekdays_list[idx])
    obj.data['Month'] = obj.data['Month'].apply(lambda idx: months_dict[idx])

    # Creating Data Frame with meekdays and months for positions statistics
    days_months = pd.concat([obj.data['Weekday'], obj.data['Month'], obj.data['Strategy'], obj.data['Position']], axis=1)
    days_months = days_months.reset_index()
    days_months = days_months.set_index('Weekday')
    days_months.drop(['Saturday', 'Sunday'], inplace=True)
    days_months.drop('Date', axis=1, inplace=True)

    # WEEKDAY STATISTICS
    days_df = days_months.copy()
    days_df = days_df.reset_index()
    days_df = days_df.set_index('Weekday')

    # empty lists for daily statistics
    d_profits = []
    d_losses = []
    d_neutrals = []
    d_profits_percent = []
    d_losses_percent = []

    # Calculating profit, loss and neutral transactions for each weekday
    # and append them to daily statistics lists
    for day in noweekends_list:
        d_profit = ((days_df.loc[day, 'Strategy'] > 0) & (days_df.loc[day, 'Position'] != 0)).sum()
        d_loss = ((days_df.loc[day, 'Strategy'] < 0) & (days_df.loc[day, 'Position'] != 0)).sum()
        d_neutral = ((days_df.loc[day, 'Strategy'] == 0) & (days_df.loc[day, 'Position'] != 0)).sum()
        d_all_transactions = d_profit + d_loss + d_neutral

        d_profits.append(d_profit)
        d_losses.append(d_loss)
        d_neutrals.append(d_neutral)
        d_profits_percent.append(100 * d_profit / d_all_transactions)
        d_losses_percent.append(100 * d_loss / d_all_transactions)

    # MONTH STATISTICS
    months_df = days_months.copy()
    months_df = months_df.reset_index()
    months_df = months_df.set_index('Month')

    m_profits = []
    m_losses = []
    m_neutrals = []
    m_profits_percent = []
    m_losses_percent = []

    # Calculating profit, loss and neutral transactions for each month
    # and append them to monthly statistics lists
    for month in months_list:
        # if file doesn't content all months, fill the missing ones with zeros
        if month != months_df.index[0]:
            m_profits.append(0)
            m_losses.append(0)
            m_neutrals.append(0)
            m_profits_percent.append(0)
            m_losses_percent.append(0)
        else:
            m_profit = ((months_df.loc[month, 'Strategy'] > 0) & (months_df.loc[month, 'Position'] != 0)).sum()
            m_loss = ((months_df.loc[month, 'Strategy'] < 0) & (months_df.loc[month, 'Position'] != 0)).sum()
            m_neutral = ((months_df.loc[month, 'Strategy'] == 0) & (months_df.loc[month, 'Position'] != 0)).sum()
            m_all_transactions = m_profit + m_loss + m_neutral

            m_profits.append(m_profit)
            m_losses.append(m_loss)
            m_neutrals.append(m_neutral)
            m_profits_percent.append(100 * m_profit / m_all_transactions)
            m_losses_percent.append(100 * m_loss / m_all_transactions)

    # Setting indexes as string type and changing the format for plotting
    obj.data.index = obj.data.index.strftime("%Y-%m-%d %H:%M")
    daily_data.index = daily_data.index.strftime("%Y-%m-%d %H:%M")

    # First and last day of trading
    first_day = obj.data.index[0]
    last_day = obj.data.index[-1]

    # CREATING INTERACTIVE PLOTLY GRAPHS
    # 1. Market equity vs strategy equity
    market_trace = go.Scatter(
        x=obj.data.index,
        y=obj.data['Market Equity'],
        name='Market Equity')

    strategy_trace = go.Scatter(
        x=obj.data.index,
        y=obj.data['Strategy Equity'],
        name='Strategy Equity')

    plot_data1 = [market_trace, strategy_trace]
    layout1 = dict(title='Market vs Strategy Equity',
                   shapes=[dict(type='line',
                                x0=first_day,
                                y0=1,
                                x1=last_day,
                                y1=1,
                                line=dict(width=0.8, color='#f30000'))])
    fig1 = dict(data=plot_data1, layout=layout1)

    # 2. Strategy returns distribution (histogram)
    strategy_histogram = go.Histogram(
        x=daily_data['Strategy'].dropna(),
        nbinsx=30)

    plot_data2 = [strategy_histogram]
    layout2 = dict(title='Daily returns distribution')
    fig2 = dict(data=plot_data2, layout=layout2)

    # 3. Weekday and month profit, loss and neutral positions (SUBPLOT)
    d_losses_trace = go.Bar(
        x=noweekends_list,
        y=d_losses,
        name='Losses',
        legendgroup='losses',
        marker=dict(color='#c70000'),
        opacity=0.8)

    d_neutrals_trace = go.Bar(
        x=noweekends_list,
        y=d_neutrals,
        name='Neutrals',
        legendgroup='neutrals',
        marker=dict(color='#b6ae00'),
        opacity=0.8)

    d_profits_trace = go.Bar(
        x=noweekends_list,
        y=d_profits,
        name='Profits',
        legendgroup='profits',
        marker=dict(color='#0a7800'),
        opacity=0.8)

    m_losses_trace = go.Bar(
        x=months_list,
        y=m_losses,
        name='Losses',
        xaxis='x2',
        yaxis='y2',
        legendgroup='losses',
        marker=dict(color='#c70000'),
        opacity=0.8,
        showlegend=False)

    m_neutrals_trace = go.Bar(
        x=months_list,
        y=m_neutrals,
        name='Neutrals',
        xaxis='x2',
        yaxis='y2',
        legendgroup='neutrals',
        marker=dict(color='#b6ae00'),
        opacity=0.8,
        showlegend=False)

    m_profits_trace = go.Bar(
        x=months_list,
        y=m_profits,
        name='Profits',
        xaxis='x2',
        yaxis='y2',
        legendgroup='profits',
        marker=dict(color='#0a7800'),
        opacity=0.8,
        showlegend=False)

    fig = py.tools.make_subplots(rows=2, cols=1)
    fig.append_trace(d_profits_trace, 1, 1)
    fig.append_trace(d_losses_trace, 1, 1)
    fig.append_trace(d_neutrals_trace, 1, 1)
    fig.append_trace(m_profits_trace, 2, 1)
    fig.append_trace(m_losses_trace, 2, 1)
    fig.append_trace(m_neutrals_trace, 2, 1)

    fig['layout'].update(title='Total sum of transactions')
    fig['layout']['yaxis2'].update(title='Months')
    fig['layout']['yaxis1'].update(title='Weekdays')

    py.offline.plot(fig, filename='daily_monthly.html')
    py.offline.plot(fig1, filename='returns.html')
    py.offline.plot(fig2, filename='histogram.html')


# if this file has been ran directly
if __name__ == "__main__":
    print('This module contains only calculating and visualization functions')
