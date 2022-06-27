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
# 5) Conditions/Strat:
#   a) For going long
#   b) For going short

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

from ProjMarcus_resampler import resampler
from ProjMarcus_strat1 import strat1
import pandas as pd

#--------------------------------<Params>--------------------------------------------------#

period_primary = '7d'
interval_primary = '15m'
period_secondary = '7d'
interval_secondary = '5m'
asset = 'ETH-USD'

sys_bal = 10000
tgt = 0.02
sl = 0.01

bt_df = resampler(asset, period_primary, interval_primary, period_secondary, interval_secondary)
bt_df = bt_df[50:]

#--------------------------------</Params>-------------------------------------------------#

def runbacktest():
    
    bt_df['Signal'] = 'No Position'         # Default Values
    bt_df['PeriodP/L'] = ((bt_df['Close_p']/bt_df['Close_p'].shift(1))-1) # % change with each candle
    bt_df['TradeP/L'] = 1                   # Default Values
    bt_df['Portfolio'] = sys_bal            # Default Values
    trade_flag = True                       # Boolean to make sure long and short trades cannot be taken simultaneuosly
    
    win_trade = 0       # Count of winning trades in the period
    loss_trade = 0      # Count of losing trades in the period
    hold_time = 0       # Total holding time(in primary candles)
    
    
    for i in range(1, len(bt_df)):          # Loop starts at 1 because the initial values in row1 need to be 0.
    
        condition = strat1(bt_df, i)        # Checking for conditions
        if(condition == 'golong' and trade_flag):
            
            
            for j in range(i,len(bt_df)-1): # j goes till length -1 because TradeP/L calc is always j+1 till the end
                trade_flag = False
                bt_df.iloc[j, bt_df.columns.get_loc('Signal')] = "Active(BUY)" # Buying at close
                hold_time += 1
                
                
                bt_df.iloc[j+1, bt_df.columns.get_loc('TradeP/L')] = (bt_df.iloc[j, bt_df.columns.get_loc('TradeP/L')]) * (1 + bt_df.iloc[j+1, bt_df.columns.get_loc('PeriodP/L')]) # Calculating the profit of active trade
                        
                
                if(bt_df.iloc[j+1, bt_df.columns.get_loc('TradeP/L')] > (1 + tgt) or bt_df.iloc[j+1, bt_df.columns.get_loc('TradeP/L')] < (1 - sl)): # Exit conditions
                    bt_df.iloc[j+1, bt_df.columns.get_loc('Signal')] = "Exit(SELL)"  # Selling at close 
                    bt_df.iloc[j+1:, bt_df.columns.get_loc('Portfolio')] = bt_df.iloc[j, bt_df.columns.get_loc('Portfolio')] * bt_df.iloc[j+1, bt_df.columns.get_loc('TradeP/L')] # Updating portfolio value
                    trade_flag = True
                    if(bt_df.iloc[j+1, bt_df.columns.get_loc('TradeP/L')] > (1 + tgt)):
                        win_trade += 1
                    if(bt_df.iloc[j+1, bt_df.columns.get_loc('TradeP/L')] < (1 - sl)):
                        loss_trade += 1
                    break # Breaking out of trade
        
            
        if(condition == 'goshort' and trade_flag):
            
            for j in range(i,len(bt_df)-1): # j goes till length -1 because TradeP/L calc is always j+1 till the end
                trade_flag = False
                bt_df.iloc[j, bt_df.columns.get_loc('Signal')] = "Active(SELL)" # Selling at close
                hold_time += 1
                
                bt_df.iloc[j+1, bt_df.columns.get_loc('TradeP/L')] = (bt_df.iloc[j, bt_df.columns.get_loc('TradeP/L')]) * (1 + bt_df.iloc[j+1, bt_df.columns.get_loc('PeriodP/L')]) # Calculating the profit of active trade
                
                if(bt_df.iloc[j+1, bt_df.columns.get_loc('TradeP/L')] > (1 + sl) or bt_df.iloc[j+1, bt_df.columns.get_loc('TradeP/L')] < (1 - tgt)): # Exit conditions
                    bt_df.iloc[j+1, bt_df.columns.get_loc('Signal')] = "Exit(BUY)"  # Buying at close 
                    bt_df.iloc[j+1:, bt_df.columns.get_loc('Portfolio')] = bt_df.iloc[j, bt_df.columns.get_loc('Portfolio')] * (1 - (bt_df.iloc[j+1, bt_df.columns.get_loc('TradeP/L')] - 1)) # Updating portfolio value
                    trade_flag = True
                    if((bt_df.iloc[j+1, bt_df.columns.get_loc('TradeP/L')] > (1 + sl))):
                       loss_trade =+ 1
                    if((bt_df.iloc[j+1, bt_df.columns.get_loc('TradeP/L')] < (1 - tgt))):
                       win_trade += 1
                       
                    break # Breaking out of trade
        
  
    return [bt_df.drop(columns = ['MA', 'StdDev', 'macd_diff']), win_trade, loss_trade]


# Calculating metrics
final_portfolio = runbacktest()[0].iloc[-1]['Portfolio']
final_pnl = runbacktest()[0].iloc[-1]['Portfolio'] - sys_bal
pnl_pct = (final_pnl/sys_bal) * 100
winning_trades = runbacktest()[1]
losing_trades = runbacktest()[2]
total_trades = winning_trades + losing_trades
win_pct = (winning_trades/total_trades) * 100


result = pd.DataFrame({"Final Portfolio": [final_portfolio], "Total P/L":[final_pnl], "P/L %":[pnl_pct], "Trades":[total_trades], "Wins":[winning_trades], "Losses":[losing_trades], "Win%":[win_pct]})

# print(runbacktest()[0][-200:-100])
# print(runbacktest()[0].iloc[-1])
print(result)

