import pandas as pd
import numpy as np
import plotly as py
import plotly.graph_objs as go
import backtest

"""
Author: Rafał Zaręba

Strategy based on stochastic oscillator
Signals:
Short position: K line crossover D line, previous K value is higher than D value and K value is above 80
Close Short position: K line crossover D line, previous K value is lower than D value
Long position: K line crossover D line, previous K value is lower than D value and K value is under 20
Close Long position: K line crossover D line, previous K value is higher than D value
"""

path = '/home/jessie/Desktop/notowaniaM1/edek123.csv'
data = pd.read_csv(path, index_col='Date', parse_dates=True)
data = data.resample('15T').bfill()
print(data.head())

# Strategy parameters
L7 = data['Low'].rolling(window=7).min()
H7 = data['High'].rolling(window=7).max()

start_hour = 8
end_hour = 18

# Creating Stochastic oscillator
K_value = ((data['Close'] - L7) / (H7 - L7)) * 100
D_value = K_value.rolling(window=3).mean()

# Creating column with hour
data['Hour'] = data.index.strftime('%H')
data['Hour'] = data.index.hour

# Creating columns with positions signals
# These columns are filled with True and False values
data['Short signal'] = (K_value < D_value) & (K_value.shift(1) > D_value.shift(1)) & (K_value > 80) &\
                       (data['Hour'] >= start_hour) & (data['Hour'] <= end_hour)
data['Short exit'] = (K_value > D_value) & (K_value.shift(1) < D_value.shift(1))
data['Long signal'] = (K_value > D_value) & (K_value.shift(1) < D_value.shift(1)) & (K_value < 20) &\
                      (data['Hour'] >= start_hour) & (data['Hour'] <= end_hour)
data['Long exit'] = (K_value < D_value) & (K_value.shift(1) > D_value.shift(1))

# Creating columns for transactions based on signals
# Short transactions: -1, Long transactions: 1, No transactions: 0
data['Short'] = np.nan
data.loc[(data['Short signal']), 'Short'] = -1
data.loc[(data['Short exit']), 'Short'] = 0

data['Long'] = np.nan
data.loc[(data['Long signal']), 'Long'] = 1
data.loc[(data['Long exit']), 'Long'] = 0

# Set 0 (no transaction) at beginning
data.iloc[0, data.columns.get_loc('Short')] = 0
data.iloc[0, data.columns.get_loc('Long')] = 0

# Fill NaN values by method forward fill
data['Long'] = data['Long'].fillna(method='ffill')
data['Short'] = data['Short'].fillna(method='ffill')

# Final Position column is sum of Long and Short column
data['Position'] = data['Long'] + data['Short']

# Market and strategy returns
data['Market Return'] = np.log(data['Close']).diff()
data['Strategy'] = data['Market Return'] * data['Position']

# Market and strategy equity
data['Market Equity'] = data['Market Return'].cumsum() + 1
data['Strategy Equity'] = data['Strategy'].cumsum() + 1

# Make a copy od data frame that contains string type index
# Only for plotting the strategy
data_s = data.copy()
data_s.index = data_s.index.strftime("%Y-%m-%d %H:%M")

first_day = data_s.index[0]
last_day = data_s.index[-1]

#

trace0 = go.Scatter(
    x=data_s.index,
    y=K_value,
    name='K Value'
)
trace1 = go.Scatter(
    x=data_s.index,
    y=D_value,
    name='D Value'
)

plot_data = [trace0, trace1]
layout = dict(title='Stochastic Oscillator',
              shapes=[dict(type='line',
                           x0=first_day,
                           y0=20,
                           x1=last_day,
                           y1=20,
                           line=dict(width=1, color='#f30000')),
                      dict(type='line',
                           x0=first_day,
                           y0=80,
                           x1=last_day,
                           y1=80,
                           line=dict(width=1, color='#f30000')),
                      ])

fig = dict(data=plot_data, layout=layout)
# py.offline.plot(fig, filename='temp_plot.html')

ratios = backtest.calculate_ratios(data, print_ratios=True)
backtest.plot_results(data, ratios)
