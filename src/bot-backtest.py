#!/usr/bin/env python3.4
import os,sys,time,curses,datetime
import logging
import cryptolib
import random

from threading import Thread
from simplesurfer import SimpleSurfer
from middlebandsurfer import MiddleBandSurfer
from btmanager import BacktestManager
from tools import Tools
from tcpsock import TcpSock
from ordermanager import OrderManager

logger = logging.getLogger('crypto')
botsel = os.getenv("bot","powr-surfer")

config = Tools.get_bot_config("mybots.yaml",botsel)
if config is None:
    print("unable to find config for {}".format(botsel))

def main(mybot):
    while True:
        try:
            mybot.process()
        except Exception as ex:
            logger.error(ex)
            #raise ex

        time.sleep(2)


if __name__ == "__main__":
    mybot = MiddleBandSurfer(config)
    ts = time.time() - ( 60 * 60 * 72 )
    ts = ts - ( ts % 3600 )
    mybot.setBackTest(ts)
    mybot.setOrderManager(OrderManager( BacktestManager() ))
    random.seed()
    port = random.randint(32000,63000)
    tcpsock = TcpSock("127.0.0.1",port,mybot)
    tcpsock.start()
    print("{} listening on {}".format(botsel,port))
    main(mybot)

