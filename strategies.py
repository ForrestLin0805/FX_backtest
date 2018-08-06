import numpy as np
import pandas as pd
import plotly as py
import plotly.graph_objs as go

"""
Author: Rafał Zaręba

Module with Forex strategies classes and functions
"""


def sma(data, period):
    """
    Function calculating simple moving average
    :param data: pandas Data Frame column
    :param period: number of periods
    :return: simple moving average SMA
    """
    return data.rolling(window=period).mean()


def ema(data, period):
    """
    Function calculating exponential moving average
    :param data: pandas Data Frame column
    :param period: number of periods
    :return: exponential moving average EMA
    """
    return data.ewm(span=period).mean()


# 2 MOVING AVERAGES STRATEGY CLASS
class MaStrategy:
    def __init__(self, market_data, interval, ma_type, s_period, l_period, start_hour, end_hour, plot_strategy=True):
        """
        Init function for setting moving average strategy parameters
        :param market_data: prepared market data with datetime index
        :param interval: time interval, 'D', 'H' or 'T'
        :param ma_type: moving average type: 'SMA' for simple or 'EMA' for exponential
        :param s_period: shorter moving average period
        :param l_period: longer moving average period
        :param start_hour: trading starting hour
        :param end_hour: trading ending hour
        :param plot_strategy: defaulf True, if True, plots the strateghy
        """
        self.data = market_data
        self.interval = interval
        self.ma_type = ma_type
        self.s_period = s_period
        self.l_period = l_period
        self.start_hour = start_hour
        self.end_hour = end_hour
        self.plot_strategy = plot_strategy

        self.ratios = None


    # Getters and setters functions
    @property
    def data(self):
        return self._data

    @property
    def ratios(self):
        return self._ratios

    @data.setter
    def data(self, data):
        self._data = data

    @ratios.setter
    def ratios(self, ratios):
        self._ratios = ratios

    def run_backtest(self):
        """
        Function calculating backtest
        Strategy based on 2 moving averages MA: shorter ma_s and longer ma_l
        Signals:
        Short position: ma_s crossover ma_l, previous value of ma_s is higher than ma_l
        Close Short position: ma_s crossover ma_l, previous value of ma_s is lower than ma_l
        Long position: ma_s crossover ma_l, previous value of ma_s is lower than ma_l
        Close Long position: ma_s crossover ma_l, previous value of ma_s is higher than ma_l
        :return: instance object with calculated data (Strategy and Strategy Return columns)
        """
        # resampling data and setting moving average type
        self.data = self.data.resample(self.interval).bfill()

        if self.ma_type == 'SMA':
            ma_s = sma(data=self.data['Close'], period=self.s_period)
            ma_l = sma(data=self.data['Close'], period=self.l_period)
        elif self.ma_type == 'EMA':
            ma_s = ema(data=self.data['Close'], period=self.s_period)
            ma_l = ema(data=self.data['Close'], period=self.l_period)
        else:
            print('Wrong ma_type passed!\n'
                  'Try: "SMA" or "EMA"')

        # Creating column with hour
        self.data['Hour'] = self.data.index.strftime('%H')
        self.data['Hour'] = self.data.index.hour

        # Creating columns with positions signals
        # These columns are filled with True and False values
        self.data['Short signal'] = (ma_s < ma_l) & (ma_s.shift(1) > ma_l.shift(1)) & \
                               (self.data['Hour'] >= self.start_hour) & (self.data['Hour'] <= self.end_hour)
        self.data['Short exit'] = (ma_s > ma_l) & (ma_s.shift(1) < ma_l.shift(1))
        self.data['Long signal'] = (ma_s > ma_l) & (ma_s.shift(1) < ma_l.shift(1)) & \
                              (self.data['Hour'] >= self.start_hour) & (self.data['Hour'] <= self.end_hour)
        self.data['Long exit'] = (ma_s < ma_l) & (ma_s.shift(1) > ma_l.shift(1))

        # Creating columns for transactions based on signals
        # Short transactions: -1, Long transactions: 1, No transactions: 0
        self.data['Short'] = np.nan
        self.data.loc[(self.data['Short signal']), 'Short'] = -1
        self.data.loc[(self.data['Short exit']), 'Short'] = 0

        self.data['Long'] = np.nan
        self.data.loc[(self.data['Long signal']), 'Long'] = 1
        self.data.loc[(self.data['Long exit']), 'Long'] = 0

        # Set 0 (no transaction) at beginning
        self.data.iloc[0, self.data.columns.get_loc('Short')] = 0
        self.data.iloc[0, self.data.columns.get_loc('Long')] = 0

        # Fill NaN values by method forward fill
        self.data['Long'] = self.data['Long'].fillna(method='ffill')
        self.data['Short'] = self.data['Short'].fillna(method='ffill')

        # Final Position column is sum of Long and Short column
        self.data['Position'] = self.data['Long'] + self.data['Short']

        # Market and strategy returns
        self.data['Market Return'] = np.log(self.data['Close']).diff()
        self.data['Strategy'] = self.data['Market Return'] * self.data['Position']

        # Market and strategy equity
        self.data['Market Equity'] = self.data['Market Return'].cumsum() + 1
        self.data['Strategy Equity'] = self.data['Strategy'].cumsum() + 1

        # If plot_strategy is equal to True, make an interactive plotly graph
        # Local, offline in web browser
        if self.plot_strategy:
            # Make a copy od data frame that contains string type index
            # Only for plotting the strategy
            data_s = self.data.copy()
            data_s.index = data_s.index.strftime("%Y-%m-%d %H:%M")

            market_trace = go.Scatter(
                x=data_s.index,
                y=data_s['Close'],
                name='Market Price',
                xaxis='x2',
                yaxis='y2')

            s_trace = go.Scatter(
                x=data_s.index,
                y=ma_s,
                name='S {} {}'.format(self.ma_type, self.s_period))

            l_trace = go.Scatter(
                x=data_s.index,
                y=ma_l,
                name='L {} {}'.format(self.ma_type, self.l_period))

            fig = py.tools.make_subplots(rows=1, cols=1, shared_xaxes=True)
            fig.append_trace(market_trace, 1, 1)
            fig.append_trace(s_trace, 1, 1)
            fig.append_trace(l_trace, 1, 1)

            fig['layout'].update(title='2 Moving Averages Strategy')
            py.offline.plot(fig, filename='ma_strategy.html')

        # return instance object
        return self


# 3 MOVING AVERAGES STRATEGY CLASS
class Ma3Strategy(MaStrategy):
    def __init__(self, market_data, interval, ma_type, s_period, l_period, exit_period,
                 start_hour, end_hour, plot_strategy=True):
        """
        Init function for setting moving average strategy parameters
        :param market_data: prepared market data with datetime index
        :param interval: time interval, 'D', 'H' or 'T'
        :param ma_type: moving average type: 'SMA' for simple or 'EMA' for exponential
        :param s_period: shorter moving average period
        :param l_period: longer moving average period
        :param exit_period: exit signal moving average period
        :param start_hour: trading starting hour
        :param end_hour: trading ending hour
        :param plot_strategy: defaulf True, if True, plots the strateghy
        """
        # Super class init method inheritance to do not duplicate the code
        super(Ma3Strategy, self).__init__(market_data, interval, ma_type, s_period,
                         l_period, start_hour, end_hour, plot_strategy)
        self.exit_period = exit_period

    def run_backtest(self):
        """
        Function calculating backtest
        Strategy based on 3 moving averages MA: shorter ma_s, longer ma_l, and exit moving average
        Signals:
        Short position: ma_s crossover ma_l, previous value of ma_s is higher than ma_l
        Close Short position: ma_exit crossover ma_s, previous value of ma_exit is lower than ma_s
        Long position: ma_s crossover ma_l, previous value of ma_s is lower than ma_l
        Close Long position: ma_exit crossover ma_s, previous value of ma_exit is higher than ma_s
        :return: instance object with calculated data (Strategy and Strategy Return columns)
        """
        # resampling data and setting moving average type
        self.data = self.data.resample(self.interval).bfill()

        if self.ma_type == 'SMA':
            ma_s = sma(data=self.data['Close'], period=self.s_period)
            ma_l = sma(data=self.data['Close'], period=self.l_period)
            ma_exit = sma(data=self.data['Close'], period=self.exit_period)
        elif self.ma_type == 'EMA':
            ma_s = ema(data=self.data['Close'], period=self.s_period)
            ma_l = ema(data=self.data['Close'], period=self.l_period)
            ma_exit = ema(data=self.data['Close'], period=self.exit_period)
        else:
            print('Wrong ma_type passed!\n'
                  'Try: "SMA" or "EMA"')

        # Creating column with hour
        self.data['Hour'] = self.data.index.strftime('%H')
        self.data['Hour'] = self.data.index.hour

        # Creating columns with positions signals
        # These columns are filled with True and False values
        self.data['Short signal'] = (ma_s < ma_l) & (ma_s.shift(1) > ma_l.shift(1)) & \
                               (self.data['Hour'] >= self.start_hour) & (self.data['Hour'] <= self.end_hour)
        self.data['Short exit'] = (ma_exit > ma_s) & (ma_exit.shift(1) < ma_s.shift(1))
        self.data['Long signal'] = (ma_s > ma_l) & (ma_s.shift(1) < ma_l.shift(1)) & \
                              (self.data['Hour'] >= self.start_hour) & (self.data['Hour'] <= self.end_hour)
        self.data['Long exit'] = (ma_exit < ma_s) & (ma_exit.shift(1) > ma_s.shift(1))

        # Creating columns for transactions based on signals
        # Short transactions: -1, Long transactions: 1, No transactions: 0
        self.data['Short'] = np.nan
        self.data.loc[(self.data['Short signal']), 'Short'] = -1
        self.data.loc[(self.data['Short exit']), 'Short'] = 0

        self.data['Long'] = np.nan
        self.data.loc[(self.data['Long signal']), 'Long'] = 1
        self.data.loc[(self.data['Long exit']), 'Long'] = 0

        # Set 0 (no transaction) at beginning
        self.data.iloc[0, self.data.columns.get_loc('Short')] = 0
        self.data.iloc[0, self.data.columns.get_loc('Long')] = 0

        # Fill NaN values by method forward fill
        self.data['Long'] = self.data['Long'].fillna(method='ffill')
        self.data['Short'] = self.data['Short'].fillna(method='ffill')

        # Final Position column is sum of Long and Short column
        self.data['Position'] = self.data['Long'] + self.data['Short']

        # Market and strategy returns
        self.data['Market Return'] = np.log(self.data['Close']).diff()
        self.data['Strategy'] = self.data['Market Return'] * self.data['Position']

        # Market and strategy equity
        self.data['Market Equity'] = self.data['Market Return'].cumsum() + 1
        self.data['Strategy Equity'] = self.data['Strategy'].cumsum() + 1

        # If plot_strategy is equal to True, make an interactive plotly graph
        # Local, offline in web browser
        if self.plot_strategy:
            # Make a copy od data frame that contains string type index
            # Only for plotting the strategy
            data_s = self.data.copy()
            data_s.index = data_s.index.strftime("%Y-%m-%d %H:%M")

            market_trace = go.Scatter(
                x=data_s.index,
                y=data_s['Close'],
                name='Market Price',
                xaxis='x2',
                yaxis='y2')

            s_trace = go.Scatter(
                x=data_s.index,
                y=ma_s,
                name='S {} {}'.format(self.ma_type, self.s_period))

            l_trace = go.Scatter(
                x=data_s.index,
                y=ma_l,
                name='L {} {}'.format(self.ma_type, self.l_period))

            exit_trace = go.Scatter(
                x=data_s.index,
                y=ma_exit,
                name='E {} {}'.format(self.ma_type, self.exit_period))

            fig = py.tools.make_subplots(rows=1, cols=1, shared_xaxes=True)
            fig.append_trace(market_trace, 1, 1)
            fig.append_trace(s_trace, 1, 1)
            fig.append_trace(l_trace, 1, 1)
            fig.append_trace(exit_trace, 1, 1)

            fig['layout'].update(title='3 Moving Averages Strategy')
            py.offline.plot(fig, filename='ma3_strategy.html')

        # return instance object
        return self


# STOCHASTIC OSCILLATOR STRATEGY CLASS
class StochasticStrategy():
    def __init__(self, market_data, interval, k_period, smooth, d_period,
                 start_hour, end_hour, plot_strategy=True):
        """
        Init function for setting stochastic oscillator strategy parameters
        :param market_data: prepared market data with datetime index
        :param interval: time interval, 'D', 'H' or 'T'
        :param k_period: back time period for calculating K value
        :param smooth: number of periods to smooth K_value
        :param d_period: K_value moving average period for calculate D_value
        :param start_hour: trading starting hour
        :param end_hour: trading ending hour
        :param plot_strategy: default True, if True, plots the strategy

        """
        self.data = market_data
        self.interval = interval
        self.k_period = k_period
        self.smooth = smooth
        self.d_period = d_period
        self.start_hour = start_hour
        self.end_hour = end_hour,
        self.plot_strategy = plot_strategy


        self.ratios = None

    # Getters and setters functions
    @property
    def data(self):
        return self._data

    @property
    def ratios(self):
        return self._ratios

    @data.setter
    def data(self, data):
        self._data = data

    @ratios.setter
    def ratios(self, ratios):
        self._ratios = ratios

    def run_backtest(self):
        """
        Function calculating backtest
        Strategy based on stochastic oscillator
        Signals:
        Short position: K line crossover D line, previous K value is higher than D value and K value is above 80
        Close Short position: K line crossover D line, previous K value is lower than D value
        Long position: K line crossover D line, previous K value is lower than D value and K value is under 20
        Close Long position: K line crossover D line, previous K value is higher than D value
        """

        # resampling data
        self.data = self.data.resample(self.interval).bfill()

        # Creating full stochastic oscillator
        low_value = self.data['Low'].rolling(window=self.k_period).min()
        high_value = self.data['High'].rolling(window=self.k_period).max()

        k_value = ((self.data['Close'] - low_value) / (high_value - low_value)) * 100
        k_value = k_value.rolling(window=self.smooth).mean()
        d_value = k_value.rolling(window=self.d_period).mean()

        # Creating column with hour
        self.data['Hour'] = self.data.index.strftime('%H')
        self.data['Hour'] = self.data.index.hour

        # Creating columns with positions signals
        # These columns are filled with True and False values
        self.data['Short signal'] = (k_value < d_value) & (k_value.shift(1) > d_value.shift(1)) & (k_value > 80) & \
                               (self.data['Hour'] >= self.start_hour) & (self.data['Hour'] <= self.end_hour)
        self.data['Short exit'] = (k_value > d_value) & (k_value.shift(1) < d_value.shift(1))
        self.data['Long signal'] = (k_value > d_value) & (k_value.shift(1) < d_value.shift(1)) & (k_value < 20) & \
                              (self.data['Hour'] >= self.start_hour) & (self.data['Hour'] <= self.end_hour)
        self.data['Long exit'] = (k_value < d_value) & (k_value.shift(1) > d_value.shift(1))

        # Creating columns for transactions based on signals
        # Short transactions: -1, Long transactions: 1, No transactions: 0
        self.data['Short'] = np.nan
        self.data.loc[(self.data['Short signal']), 'Short'] = -1
        self.data.loc[(self.data['Short exit']), 'Short'] = 0

        self.data['Long'] = np.nan
        self.data.loc[(self.data['Long signal']), 'Long'] = 1
        self.data.loc[(self.data['Long exit']), 'Long'] = 0

        # Set 0 (no transaction) at beginning
        self.data.iloc[0, self.data.columns.get_loc('Short')] = 0
        self.data.iloc[0, self.data.columns.get_loc('Long')] = 0

        # Fill NaN values by method forward fill
        self.data['Long'] = self.data['Long'].fillna(method='ffill')
        self.data['Short'] = self.data['Short'].fillna(method='ffill')

        # Final Position column is sum of Long and Short column
        self.data['Position'] = self.data['Long'] + self.data['Short']

        # Market and strategy returns
        self.data['Market Return'] = np.log(self.data['Close']).diff()
        self.data['Strategy'] = self.data['Market Return'] * self.data['Position']

        # Market and strategy equity
        self.data['Market Equity'] = self.data['Market Return'].cumsum() + 1
        self.data['Strategy Equity'] = self.data['Strategy'].cumsum() + 1

        # If plot_strategy is equal to True, make an interactive plotly graph
        # Local, offline in web browser
        if self.plot_strategy:
            # Make a copy od data frame that contains string type index
            # Only for plotting the strategy
            data_s = self.data.copy()
            data_s.index = data_s.index.strftime("%Y-%m-%d %H:%M")

            market_trace = go.Scatter(
                x=data_s.index,
                y=data_s['Close'],
                name='Market Price',
                xaxis='x2',
                yaxis='y2')

            kvalue_trace = go.Scatter(
                x=data_s.index,
                y=k_value,
                name='K Value')

            dvalue_trace = go.Scatter(
                x=data_s.index,
                y=d_value,
                name='D Value')

            data_s['20'] = 20
            data_s['80'] = 80

            line20_trace = go.Scatter(
                x=data_s.index,
                y=data_s['20'],
                name='Stochastic 20',
                line=dict(color='#c70000',
                          width=1.2,
                          dash='dash'),
                opacity=0.8)

            line80_trace = go.Scatter(
                x=data_s.index,
                y=data_s['80'],
                name='Stochastic 80',
                line=dict(color='#c70000',
                          width=1.2,
                          dash='dash'),
                opacity=0.8)

            fig = py.tools.make_subplots(rows=2, cols=1, shared_xaxes=True)
            fig.append_trace(market_trace, 1, 1)
            fig.append_trace(kvalue_trace, 2, 1)
            fig.append_trace(dvalue_trace, 2, 1)
            fig.append_trace(line20_trace, 2, 1)
            fig.append_trace(line80_trace, 2, 1)

            fig['layout'].update(title='Stochastic Oscillator Strategy')
            fig['layout']['yaxis2'].update(title='Stochastic Oscillator', tick0=0, tickvals=[0, 20, 80, 100])
            fig['layout']['yaxis1'].update(title='Market Price')

            py.offline.plot(fig, filename='stochastic_strategy.html')

        # return instance object
        return self


# if this file has been ran directly
if __name__ == "__main__":
    print('This module contains financial strategy classes and functions')
