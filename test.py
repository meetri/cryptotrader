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
from tman import TradeManager

exchange = os.getenv("EXCHANGE","USDT-BTC")

exman = ExchangeManager()
tman = TradeManager(exchange)
logger = logging.getLogger('crypto')

def draw_bot_results( stdscr, bot ):
    stdscr.clear()
    Columnize.draw_table( stdscr, 0, "name,signal,cs,last,high,low,time", [bot.get_results()] )
    lr = Columnize.cursesMultiMap(stdscr,3, bot.get_indicators())

    Columnize.draw_list( stdscr,0, 135, bot.get_debug_messages(), header="Bot Debug Messages" )

    s = []
    b = []
    for trade in bot.get_monitored_trades():
        if trade.trade_type == "sell" and trade.status not in ["cancelled"]:
            s += [trade.details()]
        elif trade.trade_type == "buy" and trade.status not in ["cancelled"]:
            b += [trade.details()]

    if len(s) > 0:
        lr = Columnize.cursesMultiMap(stdscr,lr+1, s,sameheader=True)

    if len(b) > 0:
        Columnize.cursesMultiMap(stdscr,lr+1, b,sameheader=True)

    stdscr.refresh()


def main(stdscr):
    mybot = MiddleBandSurfer(exchange,0)
    tman.monitor_trades(mybot)
    tman.start(15)
    while True:
        try:
            mybot.process()
            if mybot.signal:
                exman.bot_trade ( mybot )

            draw_bot_results(stdscr,mybot)
        except Exception as ex:
            logger.error(ex)
            raise ex

        time.sleep(2)

curses.wrapper(main)
