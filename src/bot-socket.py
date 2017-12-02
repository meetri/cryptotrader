#!/usr/bin/env python3.4
import os,sys,time,curses
import logging
import cryptolib
import random

from threading import Thread
from tools import Tools
from tcpsock import TcpSock
from ordermanager import OrderManager

logger = logging.getLogger('crypto')
botsel = os.getenv("bot","generic-backtest")
marketoverride = os.getenv("market","btc-emc2")

config = Tools.getBotConfig("mybots.yaml",botsel)

if marketoverride:
    config["bot-config"]["market"] = marketoverride.upper()

if config is None:
    print("unable to find config for {}".format(botsel))


def main(mybot):
    while True:
        try:
            mybot.process()
        except Exception as ex:
            logger.error(ex)
            #raise ex

        #time.sleep(0.5)


if __name__ == "__main__":
    mybotclass = Tools.loadClass(config["bot"])
    mybot = mybotclass( config["bot-config"] )
    if mybot:
        random.seed()
        port = config.get("_port",random.randint(32000,63000))

        om = config["exchange"]
        if isinstance(om,dict) and "name" in om:
            omname = om["name"]
        elif isinstance(om,str):
            omname = om

        exchangeclass  = Tools.loadClass(omname)
        exchange = exchangeclass(config.get("exchange-config",{}))
        if exchange:
            mybot.setOrderManager( OrderManager(exchange) )
            tcpsock = TcpSock("127.0.0.1",port,mybot)
            tcpsock.start()
            print("{}:{}:{} listening on {}".format(botsel,config["bot"],omname,port))
            main(mybot)
        else:
            print("ordermanager {} does not exist for {}".format(omname,botsel))

    else:
        print("bot {} does not exist for {}".format(config["bot"],botsel))

