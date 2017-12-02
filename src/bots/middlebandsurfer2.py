import os,sys,time
from basebot import BaseBot
from marketanalyzer import Analyzer
from exchange import Exchange
from doubleband import DoubleBand

class MiddleBandSurfer2(BaseBot):

    def __init__(self,config ):
        BaseBot.__init__(self,"MiddleBandSurfer2",config)
        self.refreshData()
        self.append_debug_message("Hello, from MiddleBandSurfer bot")


    def refreshData(self):
        self.refreshCandlesticks()



    def process(self):
        self.refreshData()
        messages = []

        ta = self.analyzer.ta

        dband = ta.dband(14,2,1.4)
        messages = dband.debug(messages)

        macd = ta.getmacd(14)

        if macd.getSignal():
            self.pushSignal("macd",macd.getSignal(),75,minor=True)

        if macd.getTrend() == "bull":
            self.pushSignal("macd-bull","buyzone",75,minor=True)


        if ta.rsi(14) <= 40 and macd.getTrend() == "bull":
            self.pushSignal("rsi14","buyzone",75,minor=True)
            if dband.enteringLowerOuterBand():
                self.pushSignal("lowband","buy",75)

            if dband.exitingLowerBand():
                self.pushSignal("lowband","buy",75)


        #self.checkSignal("rsi","overbought",60) is not None
        #if rsi.isOverbought():
        if dband.enteringUpperBand():
            self.pushSignal("upperband","sell",50)

        if dband.enteringOuterUpperBand():
            self.pushSignal("outerband","sell",75)

        if dband.risingAboveCenter():
            self.pushSignal("midband","sell",25)


        if messages:
            self.debug = []
            for msg in messages:
                self.log.info(msg)
                self.debug.append(msg)
        else:
            self.debug = ["Nothing interesting to report"]

        return BaseBot.process(self)
