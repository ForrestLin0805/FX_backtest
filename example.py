import argparse
import os
import pandas as pd
import strategies
import backtest

"""
Author: Rafał Zaręba

Example of usage 'strategies' and 'backtest' modules
to make Forex historical data strategy tests
"""

# Setting script arguments
parser = argparse.ArgumentParser()
parser.add_argument('path', help='Path to market data file', type=str)
parser.add_argument('-p', '--prepare', help='Prepare market data downloaded from Dukascopy',
                    action='store_true')
args = parser.parse_args()
path = args.path

# Prepare market data:
# if market data file is not prepared, just downloaded from Dukascopy:
if args.prepare:
    save_path = path
    data = backtest.prepare_data(path=path, save=True, save_path=save_path)
else:
    data = pd.read_csv(path, index_col='Date', parse_dates=True)

os.system('clear')
strategy_type = input('Choose strategy:\n'
                      'ma2 - for 2 moving avarages strategy\n'
                      'ma3 - for 3 moving averages strategy\n'
                      'stochastic - for stochastic oscillator strategy\n')

if strategy_type == 'ma2':
    interval = input('Enter interval : ')
    ma_type = input('Enter moving average type (SMA or EMA) : ')
    s_period = int(input('Enter period of shorter moving average : '))
    l_period = int(input('Enter period of longer moving average : '))
    start_hour = int(input('Enter start trading hour : '))
    end_hour = int(input('Enter end trading hour : '))
    plot_strategy = input('Plot strategy? (True or False) : ')

    # Starting historical data testing:
    # Creating an instance object and passing parameters
    strategy = strategies.MaStrategy(market_data=data, interval=interval, ma_type=ma_type, s_period=s_period,
                                     l_period=l_period, start_hour=start_hour, end_hour=end_hour,
                                     plot_strategy=plot_strategy)
    # Run backtest
    strategy = strategy.run_backtest()

    # Calculating ratios
    backtest.calculate_ratios(obj=strategy, print_ratios=True)

    # Plotting full results of strategy
    # Interactive charts, offline, local on web browser
    backtest.plot_results(obj=strategy)

elif strategy_type == 'ma3':
    interval = input('Enter interval : ')
    ma_type = input('Enter moving average type (SMA or EMA) : ')
    s_period = int(input('Enter period of shorter moving average : '))
    l_period = int(input('Enter period of longer moving average : '))
    exit_period = int(input('Enter period of exit moving average : '))
    start_hour = int(input('Enter start trading hour : '))
    end_hour = int(input('Enter end trading hour : '))
    plot_strategy = input('Plot strategy? (type True or False) : ')

    strategy = strategies.Ma3Strategy(market_data=data, interval=interval, ma_type=ma_type, s_period=s_period,
                                      l_period=l_period, exit_period=exit_period, start_hour=start_hour,
                                      end_hour=end_hour, plot_strategy=plot_strategy)

    strategy = strategy.run_backtest()
    backtest.calculate_ratios(obj=strategy, print_ratios=True)
    backtest.plot_results(obj=strategy)

elif strategy_type == 'stochastic':
    interval = input('Enter interval : ')
    k_period = int(input('Enter K line period : '))
    smooth = int(input('Enter smooth period : '))
    d_period = int(input('Enter D line period : '))
    start_hour = int(input('Enter start trading hour : '))
    end_hour = int(input('Enter end trading hour : '))
    plot_strategy = input('Plot strategy? (type True or False) : ')

    strategy = strategies.StochasticStrategy(market_data=data, interval=interval, k_period=k_period, smooth=smooth,
                                             d_period=d_period, start_hour=start_hour, end_hour=end_hour,
                                             plot_strategy=plot_strategy)
    strategy = strategy.run_backtest()
    backtest.calculate_ratios(obj=strategy, print_ratios=True)
    backtest.plot_results(obj=strategy)
