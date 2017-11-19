#!/usr/bin/env python3.4
import os,sys,time,curses,yaml
import logging
import json
import cryptolib

from columnize import Columnize
from middlebandsurfer import MiddleBandSurfer
from bittrex import Bittrex
from exman import ExchangeManager
from trade import Trade
from tman import TradeManager
from bottools import BotTools

logger = logging.getLogger('crypto')

def load(fn):
    print("loading {}".format(fn))
    with open(fn,"r") as stream:
        try:
            data = yaml.load(stream)
            print(data)
        except Exception as ex:
            logger.error(ex)

botsel = os.getenv("bot","btc-scraper")
config = BotTools.get_bot_config("mybots.yaml",botsel)
if config is None:
    print("unable to find config for {}".format(botname))


exman = ExchangeManager()
tman = TradeManager(config["market"])


def main(stdscr):
    mybot = MiddleBandSurfer(**config)
    tman.monitor_trades(mybot)
    tman.start(15)
    while True:
        try:
            mybot.process()
            if mybot.signal:
                exman.bot_trade ( mybot )

            BotTools.draw_bot_results(stdscr,mybot)
        except Exception as ex:
            logger.error(ex)
            #raise ex

        time.sleep(2)

curses.wrapper(main)
