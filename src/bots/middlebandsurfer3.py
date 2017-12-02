import os,sys,time
from basebot import BaseBot
from marketanalyzer import Analyzer
from exchange import Exchange
from doubleband import DoubleBand

class MiddleBandSurfer3(BaseBot):

    def __init__(self,config ):
        BaseBot.__init__(self,"MiddleBandSurfer3",config)
        self.refreshData()
        self.append_debug_message("Hello, from MiddleBandSurfer3 bot")


    def refreshData(self):
        self.refreshCandlesticks()



    def process(self):
        """
        the goal with this bot is to determine the trend,
        based on that... use the middle band as buy / sell targets
        ie. when trending up, buy at the middle, sell at the top band
        when trending down, buy at the bottom band, and sell in the middle
        """
        self.refreshData()
        ta = self.analyzer.ta
        messages = []

        dband = ta.dband(14,2,1.4)
        messages = dband.debug(messages)

        uptrend = ta.ema(50) > ta.ema(100)
        ap = (ta.atr(14) / ta.sma(20))

        if uptrend:
            messages.append("uptrending...")
            if dband.enteringLowerOuterBand():
                self.pushSignal("lowband-chomp","buy",100)
            elif dband.exitingLowerOuterBand():
                self.pushSignal("lowband-bite","buy",75)
            elif dband.settingBelowCenter():
                self.pushSignal("lowband-nibble","buy",50)


            if dband.enteringOuterUpperBand():
                self.pushSignal("upband","sell",100)
            elif dband.enteringUpperBand():
                self.pushSignal("upband","sell",75)

        else:
            messages.append("downtrending or consolidating...")
            if ta.rsi(14) <= 40 and macd.getTrend() == "bull":
                if dband.enteringLowerOuterBand():
                    self.pushSignal("lowband-chomp","buy",100)
                elif dband.exitingLowerOuterBand():
                    self.pushSignal("lowband-bite","buy",75)


            if dband.enteringOuterUpperBand():
                self.pushSignal("upband","sell",100)
            elif dband.enteringUpperBand():
                self.pushSignal("upband","sell",75)
            elif dband.risingAboveCenter():
                self.pushSignal("centerband","sell",50)


        """
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
        """


        if messages:
            self.debug = []
            for msg in messages:
                self.log.info(msg)
                self.debug.append(msg)
        else:
            self.debug = ["Nothing interesting to report"]

        return BaseBot.process(self)
