#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 26 03:26:40 2022

@author: pranav.atulya
"""

###################################################################################
# This is the resampler that feeds data to the core backtesting framework.
# resampler() takes the following as arguments:
# 1) Primary timeframe as a string Eg. 1m, 5, 15m, ...
# 2) Secondary timeframe as string(smaller candle interval)
# 3) Primary and seconday period
# 3) Name of asset(ETH, UTC, etc)

# resampler() returns a dataframe that matches all the data and indicators based on the timeseries index.
###################################################################################

from getData import getOHLC
from getIndicators import *
import pandas as pd


#--------------------------------<Params>--------------------------------------------------#

period_primary = '1mo'
interval_primary = '30m'
period_secondary = '1mo'
interval_secondary = '15m'
asset = 'BTC-USD'

#--------------------------------</Params>-------------------------------------------------#




def resampler(asset, period_primary, interval_primary, period_secondary, interval_secondary):
# Get price data from dataAPI
    df1 = getOHLC(asset, period = period_primary, interval = interval_primary, suffix = '')
    df2 = getOHLC(asset, period = period_secondary, interval = interval_secondary, suffix = '')

# Add indicators
    df1 = getSMA(df1)
    df1 = getBollingerBands(df1)
    df1 = getMACD(df1)

    df2 = getSMA(df2)
    
    
    
# Left join and merge dataframes    
    df_resampled = pd.merge(df1, df2, how = 'left', on = 'Datetime', suffixes = ('_p', '_s'))
    # df_resampled['index'] = [i for i in range(0,len(df_resampled))]
    # df_resampled.set_index('index', drop = False, inplace = True)
    

    return df_resampled


# print(resampler(asset, period_primary, interval_primary, period_secondary, interval_secondary))
