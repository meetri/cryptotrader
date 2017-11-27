import os,sys,time
from basebot import BaseBot
from marketanalyzer import Analyzer
from exchange import Exchange

class SimpleSurfer(BaseBot):

    #def __init__(self,market,budget,tradelimit,candlestick="5m",timeframe="24h"):
    def __init__(self,config ):
        BaseBot.__init__(self,"SimpleSurfer",config)#market,budget,tradelimit,candlestick,timeframe,"SimpleSurfer")
        self.refreshData()
        self.append_debug_message("Hello, from SimpleSurfer bot")


    def refreshData(self):
        self.refreshCandlesticks()
        self.analyzer.addIndicator("macd",{})
        self.analyzer.addIndicator("bbands",{"timeperiod":20,"nbdevup":2,"nbdevdn":2})
        self.analyzer.addIndicator("atr",{"period":14})
        self.analyzer.addIndicator("rsi",{"overbought":63,"oversold":40,"period":14})
        self.analyzer.process()


    def process(self):
        self.refreshData()

        macd = self.analyzer.getIndicator("macd")
        bbands = self.analyzer.getIndicator("bbands")
        rsi = self.analyzer.getIndicator("rsi")
        atr = self.analyzer.getIndicator("atr")

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
        if self.analyzer.last("closed",2) < bbands.middle(2) and self.analyzer.last("closed") > bbands.middle():
            messages.append("price is moving above middle band")

        if self.analyzer.last("closed",2) > bbands.middle(2) and self.analyzer.last("closed") < bbands.middle():
            messages.append("price is moving below middle band")

        if self.analyzer.last("closed") > bbands.top():
            messages.append("price is above top band")

        if self.analyzer.last("closed") < bbands.low():
            messages.append("price is below the lower band")

        if (self.analyzer.last("closed",2) > bbands.top(2) and
                self.analyzer.last("closed") > bbands.top()):
            messages.append("price is moving strong above top band")

        if (self.analyzer.last("closed",2) < bbands.low(2) and
                self.analyzer.last("closed") < bbands.low()):
            messages.append("price is moving strong below lower band")


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


        if messages:
            self.debug = []
            for msg in messages:
                self.debug.append(msg)
        else:
            self.debug = ["Nothing interesting to report"]

        return BaseBot.process(self)
