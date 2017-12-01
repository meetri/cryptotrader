import os,sys,time
from basebot import BaseBot
from marketanalyzer import Analyzer
from exchange import Exchange
from doubleband import DoubleBand

class MiddleBandSurfer2(BaseBot):

    #def __init__(self,market,budget,tradelimit,candlestick="5m",timeframe="24h"):
    def __init__(self,config ):
        BaseBot.__init__(self,"MiddleBandSurfer2",config)#market,budget,tradelimit,candlestick,timeframe,"SimpleSurfer")
        self.refreshData()
        self.append_debug_message("Hello, from MiddleBandSurfer bot")


    def refreshData(self):
        self.refreshCandlesticks()
        """
        self.analyzer.addIndicator("MACD",{})
        self.analyzer.addIndicator("BBands",{"timeperiod":20,"nbdevup":2,"nbdevdn":2})
        self.analyzer.addIndicator("BBands",{"timeperiod":20,"nbdevup":1.5,"nbdevdn":1.5,"label":"iBBands","chartcolors":["#AA0000","00AA00","0000AA"]},"iBBand")
        self.analyzer.addIndicator("ATR",{"period":14})
        self.analyzer.addIndicator("RSI",{"overbought":63,"oversold":40,"period":14})
        self.analyzer.process()
        """



    def process(self):
        self.refreshData()
        messages = []

        ta = self.analyzer.ta

        dband = ta.dband(14,2,1.5)
        dband.debug(messages)

        #TODO adjust this logic based on trend slope determined by a SMA

        if ta.rsi(14) <= 40:
            if dband.enteringLowerOuterBand():
                self.pushSignal("lowband","buy",75)

            if dband.enteringLowerBand():
                self.pushSignal("lowband","buy",50)

            if dband.risingAboveCenter():
                self.pushSignal("midband","buy",25)

            if dband.settingBelowCenter():
                self.pushSignal("midband","buy",25)


        #self.checkSignal("rsi","overbought",60) is not None
        #if rsi.isOverbought():
        if dband.enteringUpperBand():
            self.pushSignal("upperband","sell",50)

        if dband.enteringOuterUpperBand():
            self.pushSignal("upperband","sell",75)

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
