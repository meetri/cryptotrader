#!/usr/local/bin/python3 -u
"""
scrape jobs retrieved from queue
"""

import os,sys,time,redis,json,numpy,curses
import talib
import concurrent.futures
import logging


curdir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(curdir + "/modules")
sys.path.append(curdir + "/datasources")
sys.path.append(curdir + "/exchangeapis")
sys.path.append(curdir + "/indicators")

from holdingmonitor import HoldingMonitor
from columnize import Columnize
from mybots import BotMaster
from wallet import Wallet

logger = logging.getLogger('crypto')
hdlr = logging.FileHandler('/tmp/crypto.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)

botmaster = BotMaster()
wallet = Wallet()

"""
wallet.manage_trade({
    "signal": "oversold",
    "exchange": "bittrex",
    "market": "USDT-BTC",
    "price_entry": 3965,
    "trade_amount": 0.1,
    "trade_fee": 0.0025
    })
"""

def main(stdscr):
    while True:
        stdscr.clear()
        botsignal = botmaster.middleBandSurfer("USDT")
        res = wallet.manage_trade(botsignal)

        Columnize.cursesMapRow( stdscr, 0  ,botsignal.data["result"]["details"] )
        idx = 0
        for indicator in botsignal.data["indicators"]:
            Columnize.cursesMapRow( stdscr, idx + 1, indicator, xofs=2 )
            idx += 1

        curline = 2 + len(botsignal.data["indicators"])
        active_trades = wallet.get_active_trades()
        if active_trades is not None:
            row = []
            for idx,trade in enumerate(active_trades):
                row += [wallet.analyze_trade(idx)]

            Columnize.cursesMultiMap( stdscr, curline , row )

        curline = curline + len(row) + 2
        best_trades = botsignal.botdata["bestbuy"]["processing"]
        if best_trades is not None:
            row = []
            for key in best_trades:
                row += [best_trades[key]]

            Columnize.cursesMultiMap( stdscr, curline , row )


        stdscr.refresh()
        time.sleep(1)


curses.wrapper(main)
