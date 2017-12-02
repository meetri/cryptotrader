import os,sys,time
from basebot import BaseBot
from marketanalyzer import Analyzer
from exchange import Exchange
from doubleband import DoubleBand

class MA2Bot(BaseBot):

    def __init__(self,config ):
        config["candlestick"] = config.get("candlestick","5m")
        config["timeframe"] = config.get("timeframe","48h")
        BaseBot.__init__(self,"MABot",config)


    def refreshData(self):
        self.refreshCandlesticks()


    def process(self):
        self.refreshData()
        ta = self.analyzer.ta

        uptrend = False
        if ta.ema(20) > ta.ema(40):
            uptrend = True

        ap = (ta.atr(20) / ta.sma(50)) * 100
        bbwidth = ta.getbband().width()

        return {
                "market": self.getMarket(),
                "last": "{:.08f}".format(self.analyzer.last("closed")),
                "slope": ta.getbband(20).getSlope(30),
                "uptrend": uptrend,
                "atr": "{:.08f}".format(ta.atr(20)),
                "sma": "{:.08f}".format(ta.sma(50)),
                "atrPercent": "{:.04f}".format(ap),
                "bbwidth": "{:.08f}".format(bbwidth)
                }

