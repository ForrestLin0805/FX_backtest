import pandas as pd
import strategies
import backtest

"""
Author: Rafał Zaręba

Example of usage 'strategies' and 'backtest' modules
to make Forex historical data strategy tests
"""
# Prepare market data:

# if market data file is already prepared:
path = '/home/user/Desktop/FX_backtest/eurusd_prepared.csv'
data = pd.read_csv(path, index_col='Date', parse_dates=True)

# if market data file is not prepared, just downloaded from Dukascopy:
# path = '/home/user/Desktop/dukascopy/eurusd_notprepared.csv'
# save_path = '/home/user/Desktop/dukascopy/eurusd_prepared.csv'
# data = backtest.prepare_data(path=path, save=True, save_path=save_path)

# Starting historical data testing:
# 1. 2 SIMPLE MOVING AVERAGES STRATEGY TEST

# Creating an instance object and passing parameters
strategy1 = strategies.MaStrategy(market_data=data, interval='15T', ma_type='SMA', s_period=8, l_period=61,
                                  start_hour=9, end_hour=18, plot_strategy=True)
# Run backtest
strategy1.run_backtest()

# Calculating ratios
backtest.calculate_ratios(obj=strategy1, print_ratios=True)

# Plotting full results of strategy
# Interactive charts, offline, local on web browser
backtest.plot_results(obj=strategy1)

# 2. 3 SIMPLE MOVING AVERAGES STRATEGY TEST
strategy2 = strategies.Ma3Strategy(market_data=data, interval='15T', ma_type='SMA', s_period=10, l_period=20,
                                   exit_period=6, start_hour=8, end_hour=18, plot_strategy=True)

strategy2.run_backtest()
backtest.calculate_ratios(obj=strategy2, print_ratios=True)
backtest.plot_results(obj=strategy2)

# 3. FULL STOCHASTIC OSCILLATOR STRATEGY TEST
strategy3 = strategies.StochasticStrategy(market_data=data, interval='15T', k_period=7, smooth=1, d_period=3,
                                          start_hour=8, end_hour=18, plot_strategy=True)
strategy3 = strategy3.run_backtest()
backtest.calculate_ratios(obj=strategy3, print_ratios=True)
backtest.plot_results(obj=strategy3)