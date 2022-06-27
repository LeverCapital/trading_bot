#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 14 01:25:32 2022

@author: pranav.atulya
"""

###################################################################################
# Basic Initial strat
# Indicators used: Bollinger bands, MACD, Simple moving average, OLS regression channel 
# Data feed: Close price, period: last 1 month, interval: 5min(primary), 1min(confirmation) (May change later based on backtest results)
# Entry condition; BUY/GoLong: (50SMA > UBB) and (MACD_FastLine < MACD_FastLine_mean - MACD_FastLine_stdev) and (Close > UC)
# Entry condition cofirmation; BUY/GoLong: (Close_1min > 50SMA_1min)
# Entry condition; SELL/GoShort: *exact opposite of the buy conditions.

# strat1 takes two dataframes, one for each interval(primary and confirmation); 
# It requires the dataframes to have the close price and all the indicator values as separate columns
###################################################################################

def strat1(bt_df, i):
    
    macd_mean = bt_df['signal_line'].mean() # Assumes that the MACD values stay in a given range for each asset
    macd_std = bt_df['signal_line'].std()
    
    if(bt_df['SMA50_p'][i] > bt_df['Upper Band'][i] and bt_df['signal_line'][i] < macd_mean-1*macd_std):
        
        if(bt_df['SMA50_s'][i] < bt_df['Close_s'][i]):
            return "golong"
        else:
            pass
    else:
        pass
    
    if(bt_df['SMA50_p'][i] < bt_df['Lower Band'][i] and bt_df['signal_line'][i] > macd_mean+1*macd_std):
        
        if(bt_df['SMA50_s'][i] > bt_df['Close_s'][i]):
            return "goshort"
        else:
            return False
    else:
        return False
        
        