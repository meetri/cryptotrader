#!/usr/local/bin/python3 -u
"""
scrape jobs retrieved from queue
"""

import os,sys,time,redis,json,numpy
import talib
import concurrent.futures

curdir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(curdir + "/modules")
sys.path.append(curdir + "/datasources")
sys.path.append(curdir + "/exchangeapis")

from trader import Trader
from influxdbwrapper import InfluxDbWrapper

db = InfluxDbWrapper.getInstance()

#btcBot = Trader("USDT-BTC")
btcBot = Trader("BTC-TRIG")
cs  = btcBot.get_candlesticks("24h","1m")
for i in range(0,btcBot.get_indicator_size()):
    try:
        print("getting indicator {}".format(i))
        res = btcBot.get_indicator_index(i)
        db.bulkAddTA("bittrex",btcBot.market,"1m",res)
    except Exception as ex:
        print("bottest exception: {}".format(ex))

res = db.bulkSave()
#print ( res )
