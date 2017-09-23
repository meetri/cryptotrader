#!/usr/local/bin/python3 -u
"""
schedule scraping of crypto exchange data based on enabled elements in postgres:crypto->markets->??
"""

import os,sys,time,redis

curdir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(curdir + "/modules")
sys.path.append(curdir + "/datasources")
sys.path.append(curdir + "/exchangeapis")

from exchangedata import ExchangeDataHandler

# set defaults
sleep_interval = int(os.getenv("POLL_INTERVAL","10"))

# configure via environment variable settings
dataHandler = ExchangeDataHandler().getInstance()

marketlist = dataHandler.getMarketList().split(" ")
while 1:
    for market in marketlist:
        dataHandler.pushMarketQueue( market )
    print("{} markets pushed to queue".format( len(marketlist) ) )
    time.sleep( sleep_interval )
