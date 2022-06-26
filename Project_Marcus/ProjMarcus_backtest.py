#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 26 02:56:48 2022

@author: pranav.atulya
"""

###################################################################################
# This is the core backtesting framework to backtest strategies.
# runbacktest() takes the following as arguments:
# 1) Daframe containing the following columns:
#   a) Price; Primary, Secondary timeframe candles(Resampled to match for the given two timeseries)
#   b) Indicators: Each indicator will have a separate column(Resampled to match for two timeseries)
# 2) Initial portfolio balance
# 3) Target%
# 4) Stoploss%

# runbacktest() will return the following as dictionary:
# 1) Porfolio end value
# 2) Absolute Profit/Loss
# 3) Percentage Profit/Loss
# 4) Total trades taken
# 5) Average duration of each trade
# 6) Total winning trades
# 7) Win ratio

# Note: Any strategy that has more than one timeseries should have the primary as the largest candle interval. 
#       runbacktest() only gets dataframes from the ProjMarcus_resampler.py
###################################################################################



