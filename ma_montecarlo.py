import pandas as pd
import numpy as np
import backtest
import strategies

"""
Author: Rafał Zaręba

Monte Carlo simulation used to find the best match of moving averages periods
in 2 moving averages strategy. It generates random numbers and set them as moving averages
lengths, then calculates strategy ratios for each case. User can set manually
number of simulations and priority (maximum profit of strategy or minimum capital drawdown) 
"""

# Uploading market data
path = '/home/user/Desktop/dukascopy/eurusd_prepared.csv'
data = pd.read_csv(path, index_col='Date', parse_dates=True)

# Simulation parameters
simulations_num = 100
priority = 'return'
ma_type = 'SMA'
start_hour = 8
end_hour = 18
interval = '15T'


# Creating empty array to store moving average combinations
# 2 columns and (simulations_num) * rows, set as int type
ma_array = np.zeros((simulations_num, 2))
ma_array.astype(int)

# Creating empty arrays to store calculated ratios for each simulation
strategy_return_arr = np.zeros(simulations_num)
max_drawdown_arr = np.zeros(simulations_num)

# For loop iterates simulations_num times
# generating random moving averages, doing a strategy backtest
# and stores calculated ratios in arrays
for i in range(simulations_num):

    # generating random moving averages
    # if they are the same, add one to the second MA
    ma_random = np.random.random_integers(8, 80, (1, 2))
    if ma_random[0][0] == ma_random[0][1]:
        ma_random[0][1] += 1

    ma_array[i:] = ma_random

    # Creating an instance object of MaStrategy class and pass set and generated parameters
    strategy = strategies.MaStrategy(market_data=data, interval=interval, ma_type=ma_type,
                                     s_period=ma_random[0][0], l_period=ma_random[0][1],
                                     start_hour=start_hour, end_hour=end_hour, plot_strategy=False)

    strategy = strategy.run_backtest()
    backtest.calculate_ratios(strategy, print_ratios=False)
    ratios = strategy.ratios

    # Appending calculated ratios to arrays
    strategy_return = ratios[1]
    max_drawdown = ratios[2]
    strategy_return_arr[i:] = strategy_return
    max_drawdown_arr[i:] = max_drawdown

# Print best configuration, depends on priority
if priority == 'return':
    best_argument = strategy_return_arr.argmax()
    print('Priority: The highest strategy return\n'
          'Max strategy return: {:1.2f}%\n'
          'Capital Drawdown: {:1.2f}\n'
          'moving average periods: {}'.format(strategy_return_arr[best_argument]*100,
                                              max_drawdown_arr[best_argument], ma_array[best_argument]))
elif priority == 'drawdown':
    best_argument = max_drawdown_arr.argmin()
    print('Priority: The lowest capital drawdown\n'
          'The lowest capital drawdown: {:1.2f}%\n'
          'Strategy return: {:1.2f}\n'
          'moving average periods: {}'.format(max_drawdown_arr[best_argument],
                                              strategy_return_arr[best_argument]*100, ma_array[best_argument]))

# Store the best moving averages periods in vars
best_s_period = int(ma_array[best_argument][0])
best_l_period = int(ma_array[best_argument][1])

# Run full backtest with best arguments
fulltest = strategies.MaStrategy(market_data=data, interval=interval, ma_type=ma_type,
                                 s_period=best_s_period, l_period=best_l_period, start_hour=start_hour,
                                 end_hour=end_hour, plot_strategy=True)
fulltest = fulltest.run_backtest()
backtest.plot_results(fulltest)






