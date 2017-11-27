import os,sys,time
from basebot import BaseBot
from marketanalyzer import Analyzer
from exchange import Exchange
from doubleband import DoubleBand

class MiddleBandSurfer(BaseBot):

    #def __init__(self,market,budget,tradelimit,candlestick="5m",timeframe="24h"):
    def __init__(self,config ):
        BaseBot.__init__(self,"MiddleBandSurfer",config)#market,budget,tradelimit,candlestick,timeframe,"SimpleSurfer")
        self.refreshData()
        self.append_debug_message("Hello, from MiddleBandSurfer bot")


    def refreshData(self):
        self.refreshCandlesticks()
        self.analyzer.addIndicator("macd",{})
        self.analyzer.addIndicator("bbands",{"timeperiod":20,"nbdevup":2,"nbdevdn":2})
        self.analyzer.addIndicator("bbands",{"timeperiod":20,"nbdevup":1.5,"nbdevdn":1.5,"label":"iBBands","chartcolors":["#AA0000","00AA00","0000AA"]},"iBBand")
        self.analyzer.addIndicator("atr",{"period":14})
        self.analyzer.addIndicator("rsi",{"overbought":63,"oversold":40,"period":14})
        self.analyzer.process()


    def process(self):
        self.refreshData()

        macd = self.analyzer.getIndicator("macd")
        bbands = self.analyzer.getIndicator("bbands")
        ibbands = self.analyzer.getIndicator("iBBand")
        rsi = self.analyzer.getIndicator("rsi")
        atr = self.analyzer.getIndicator("atr")

        dband = DoubleBand(self.analyzer,outer=bbands,inner=ibbands)


        self.pushSignal("rsi","oversold",rsi.isOversold(),minor=True)
        self.pushSignal("rsi","overbought",rsi.isOverbought(),minor=True)


        """
        #check if price is rising and closes above the middle band
        if ( self.analyzer.last("closed",3) < bbands.middle() and
                self.analyzer.last("closed",2) > bbands.middle() and
                self.analyzer.last("closed") > bbands.middle() and
                self.checkSignal("rsi","oversold",60) is not None ):
            self.pushSignal("bband1","buy",10)

        #check if price is dropping and closes below the middle band
        if ( self.analyzer.last("closed",3) > bbands.middle() and
                self.analyzer.last("closed",2) < bbands.middle() and
                self.analyzer.last("closed") < bbands.middle() and
                self.checkSignal("rsi","overbought",60) is not None ):
            self.pushSignal("bband2","sell",10)
        """

        messages = []

        if dband.enteringLowerBand():
            messages.append("entering lower band")
        if dband.exitingLowerOuterBand():
            messages.append("exiting lower outer band")
        if dband.enteringLowerOuterBand():
            messages.append("entering lower outer band")
        if dband.exitingLowerOuterBand():
            messages.append("exiting lower outer band")
        if dband.risingAboveCenter():
            messages.append("rising above center")
        if dband.enteringUpperBand():
            messages.append("entering upper band")
        if dband.exitingOuterUpperBand():
            messages.append("exiting outer upper band")
        if dband.enteringOuterUpperBand():
            messages.append("entering outer upper band")
        if dband.exitingUpperBand():
            messages.append("exiting upper band")
        if dband.settingBelowCenter():
            messages.append("setting below center")


        #TODO adjust this logic based on trend slope determined by a SMA

        #self.checkSignal("rsi","oversold",60) is not None
        if rsi.isOversold():
            if dband.enteringLowerOuterBand():
                self.pushSignal("lowband","buy",75)

            if dband.enteringLowerBand():
                self.pushSignal("lowband","buy",50)

            if dband.risingAboveCenter():
                self.pushSignal("midband","buy",25)


        #self.checkSignal("rsi","overbought",60) is not None
        if rsi.isOverbought():
            if dband.enteringUpperBand():
                self.pushSignal("upperband","sell",50)

            if dband.enteringOuterUpperBand():
                self.pushSignal("upperband","sell",75)

        """
        #check if price goes below the lower band
        if ( self.analyzer.last("closed") < bbands.low() and
                self.checkSignal("rsi","oversold",60) is not None ):
            messages.append("buy signal triggered")
            self.pushSignal("bbandLow","buy",50)

        #check if price high goes above the top bband
        if ( self.analyzer.last("high") > bbands.top() and
                self.checkSignal("rsi","overbought",60) is not None ):
            messages.append("sell signal triggered")
            self.pushSignal("bbandHigh","sell",50)
        """


        if messages:
            self.debug = []
            for msg in messages:
                self.log.info(msg)
                self.debug.append(msg)
        else:
            self.debug = ["Nothing interesting to report"]

        return BaseBot.process(self)
