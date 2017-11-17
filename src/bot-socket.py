#!/usr/bin/env python3.4
import os,sys,time,curses,yaml
import logging
import cryptolib
import random

from threading import Thread

from columnize import Columnize
from middlebandsurfer import MiddleBandSurfer
from bittrex import Bittrex
from exman import ExchangeManager
from trade import Trade
from tman import TradeManager
from bottools import BotTools
from tcpsock import TcpSock

logger = logging.getLogger('crypto')

def load(fn):
    print("loading {}".format(fn))
    with open(fn,"r") as stream:
        try:
            data = yaml.load(stream)
            print(data)
        except Exception as ex:
            logger.error(ex)


config = BotTools.get_bot_config("mybots.yaml","btc-scraper")
if config is None:
    print("unable to find config for {}".format(botname))


exman = ExchangeManager()
tman = TradeManager(config["market"])


def main(mybot):
    tman.monitor_trades(mybot)
    tman.start(15)
    while True:
        try:
            mybot.process()
            if mybot.signal:
                exman.bot_trade ( mybot )

            #BotTools.draw_bot_results(stdscr,mybot)
        except Exception as ex:
            logger.error(ex)
            #raise ex

        time.sleep(2)


if __name__ == "__main__":
    mybot = MiddleBandSurfer(**config)
    random.seed()
    port = random.randint(32000,63000)
    tcpsock = TcpSock("127.0.0.1",port,mybot)
    tcpsock.start()
    #logger.info("{} listening on {}".format(mybot.get_name(),port))
    print("{} listening on {}".format(mybot.get_name(),port))
    main(mybot)

