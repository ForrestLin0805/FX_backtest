import pandas as pd
import numpy as np
import backtest
import strategies

"""
Author: Rafał Zaręba

Monte Carlo simulation used to find the best match k_period, smooth and d_period
in stochastic oscillator strategy. It generates random numbers and set them as parameters
then calculates strategy ratios for each case. User can set manually
number of simulations and priority (maximum profit of strategy or minimum capital drawdown) 
"""

# Uploading market data
path = '/home/user/Desktop/FX_backtest/eurusd_prepared.csv'
data = pd.read_csv(path, index_col='Date', parse_dates=True)

# Simulation parameters
simulations_num = 100
priority = 'return'
start_hour = 8
end_hour = 18
interval = '15T'


# Creating empty array to store k,d and smooth combinations
# 3 columns and (simulations_num) * rows, set as int type
vals_array = np.zeros((simulations_num, 3))
vals_array.astype(int)

# Creating empty arrays to store calculated ratios for each simulation
strategy_return_arr = np.zeros(simulations_num)
max_drawdown_arr = np.zeros(simulations_num)

# For loop iterates simulations_num times
# generating k,d and smooth values, doing a strategy backtest
# and stores calculated ratios in arrays
for i in range(simulations_num):

    # generating random k, smooth and d values and store them in array
    vals_random = np.random.random_integers(3, 20, (1, 3))
    vals_array[i:] = vals_random

    # Creating an instance object of StochasticStrategy class and pass set and generated parameters
    strategy = strategies.StochasticStrategy(market_data=data, interval=interval, k_period=vals_random[0][0],
                                             smooth=vals_random[0][1], d_period=vals_random[0][2],
                                             start_hour=start_hour, end_hour=end_hour, plot_strategy=False)
    strategy = strategy.run_backtest()
    backtest.calculate_ratios(obj=strategy, print_ratios=False)
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
          'values: [k, smooth, d]{} :'.format(strategy_return_arr[best_argument]*100,
                                              max_drawdown_arr[best_argument], vals_array[best_argument]))
elif priority == 'drawdown':
    best_argument = max_drawdown_arr.argmin()
    print('Priority: The lowest capital drawdown\n'
          'The lowest capital drawdown: {:1.2f}%\n'
          'Strategy return: {:1.2f}\n'
          'values: [k, smooth, d]{} :'.format(strategy_return_arr[best_argument]*100,
                                              max_drawdown_arr[best_argument], vals_array[best_argument]))

# Store the best k, smooth and d values in vars
best_k_period = int(vals_array[best_argument][0])
best_smooth = int(vals_array[best_argument][1])
best_d_period = int(vals_array[best_argument][2])

# Run full backtest with best arguments
fulltest = strategies.StochasticStrategy(market_data=data, interval=interval, k_period=best_k_period,
                                         smooth=best_smooth, d_period=best_d_period, start_hour=start_hour,
                                         end_hour=end_hour, plot_strategy=True)
fulltest = fulltest.run_backtest()
backtest.plot_results(fulltest)


