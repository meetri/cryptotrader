#!/usr/bin/env python3.4
import os,sys,time,curses
import logging
import json
import cryptolib

from columnize import Columnize
from middlebandsurfer import MiddleBandSurfer
from bittrex import Bittrex
from exman import ExchangeManager
from trade import Trade

exman = ExchangeManager()
logger = logging.getLogger('crypto')

"""
trade = Trade({
        "exchange": "bittrex",
        "market": "USDT-BTC",
        "quantity": 0.0001,
        "price": 3000.00,
        "trade_type": "buy",
    })


r = exman.perform_trade(trade)
print( json.dumps(trade.meta))
sys.exit()

trades = Trade.load_by_id(66)
trades[0].cancel()
print( json.dumps(trades[0].meta))

"""

#def market2_selllimit( self, market,qty,rate, ordertype="LIMIT",timeineffect="IMMEDIATE_OR_CANCEL",condition="NONE",target=0):
#cs = Bittrex().public_get_candles().getData()
#res = Bittrex().market2_tradebuy("USDT-BTC",0.0001,3530)
#res = Bittrex().market_buymarket("USDT-BTC",0.0001).getData()
"""
res = Bittrex().account_get_order("021ee90e-b447-46dd-86c9-b0522e90d392").getData()
print(res)
res = Bittrex().market_buylimit("USDT-BTC",0.0001,3500).getData()
if res["success"]:
    uuid = res["result"]["uuid"]
    res = Bittrex().account_get_order(uuid).getData()
    print(res)
"""

#print(res.getData())
#sys.exit()

def draw_bot_results( stdscr, bot ):
    stdscr.clear()
    Columnize.draw_table( stdscr, 0, "name,signal,last,time", [bot.get_results()] )
    lr = Columnize.cursesMultiMap(stdscr,3, bot.get_indicators())

    t = []
    for trade in bot.get_monitored_trades():
        t += [trade.details()]

    Columnize.cursesMultiMap(stdscr,lr+1, t,sameheader=True)
    stdscr.refresh()


def main(stdscr):
    mybot = MiddleBandSurfer("USDT-BTC")
    while True:
        try:
            mybot.process()
            if mybot.signal:
                exman.bot_trade ( mybot )

            draw_bot_results(stdscr,mybot)
        except Exception as ex:
            logger.error(ex)

        time.sleep(2)

curses.wrapper(main)
