#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 27 13:14:11 2021

@author: pranav.atulya
"""

import yfinance as yf

def getOHLC(stock, period, interval, suffix = ""):
    stock = stock+suffix
    tickr = yf.Ticker(stock)
    hist = tickr.history(period, interval)
    hist=hist.drop(['Dividends', 'Stock Splits','Open', 'High', 'Low', 'Volume'], axis=1)
    return hist






#-------------- Set Paramenters--------------#

# stock = 'BTC-USD'
# period = '1mo' # '1mo'. '6mo'
# interval = '5m' #“1m”, “2m”, “5m”, “15m”, “30m”, “60m”, “90m”, “1h”, “1d”, “5d”, “1wk”, “1mo”, “3mo” 
# suffix = ""
# ohlc = getOHLC(stock, period, interval, suffix = '').dropna()
# print(ohlc.tail())
# print(ohlc['Close'][-1])
# # print(ohlc['Close'][0])
# # print((ohlc['Close'][-1] - ohlc['Close'][0])/)
# ohlc.to_csv('/Users/pranav.atulya/Desktop/N_etf.csv')
# print(len(ohlc))