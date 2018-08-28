# FX_backtest
This repository contains forex historical data strategies testing modules.
Example of ready to use, prepared data from function 'prepare_data' attached to repository: "eurusd_prepared.csv" 

Make sure, you have installed necessary packages:
- matplotlib,
- plotly,
- pandas,
- numpy,
- seaborn

Example of usage:
1. Run strategy with known parameters and prepared data:
Run in terminal:
- python forex.py /home/user/Desktop/FX_backtest/eurusd_prepared.csv

2. Run strategy with known parameters and unprepared data (downloaded from Dukascopy)
Run in terminal:
- python forex.py -p /home/user/Desktop/FX_backtest/eurusd.csv

3. Run montecarlo simulations:
- python ma_montecarlo.py /home/user/Desktop/FX_backtest/eurusd.csv

Script will automatically ask the user about all needed parameters.

Note:
Interval must be entered as: 15T for 15 minutes, 1H for 1 hour etc. 



