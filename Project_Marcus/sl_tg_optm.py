#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 22 13:32:19 2022

@author: pranav.atulya
"""

##############################################################################

# This is a brute force optimizer. It displays the performance metrics of a strat for a given combination of Target and Stoploss for a given window.

# optm_primary takes the following arguments:
# 1) List containing the upper and lower bound of Target values
# 2) List containing the upper and lower bound of Stoploss values
# 3) Step size of Target
# 4) Step size of Stoploss
# 5) The strat to be backtested

# optm_primary returns a sorted dictionary with following keys:
# 1) Porfolio end value
# 2) Absolute Profit/Loss
# 3) Percentage Profit/Loss
# 4) Total trades taken
# 5) Average duration of each trade
# 6) Total winning trades
# 7) Win ratio

##############################################################################


from getData import getOHLC
from getIndicators import *
from OLS import OLS_max

# Params:
tgt = []
sl = []
step_tgt = 0.2
step_sl = 0.2



def optm_primary():
    # Call