import os,sys,time
from basebot import BaseBot
from marketanalyzer import Analyzer

class MiddleBandSurfer(BaseBot):

    def __init__(self,market):
        BaseBot.__init__(self,market,"MiddleBandSurfer")


    def process(self):
        BaseBot.process(self)
        """
        this bot will first check the slope of the 50/sma and BBands middle band making sure it's in an incline,
        then it will check if a candle from above touces the center line. It will then execute a buy to best buy bot to trail the buy signal to it's bottom
        the sell middleBandSurferSell counterpart bot will profit is above margin and price touches the upper band. It will then go to best sell bot to trail
        the price higher for the ideal sell
        """

        self.csdata = self.trader.get_candlesticks("24h","5m")
        analyzer = Analyzer( self.csdata )

        analyzer.add_indicator("macd",{})
        analyzer.add_indicator("bbands",{})
        analyzer.add_indicator("sma",{})
        analyzer.add_indicator("rsi",{"overbought":70,"oversold":30,"period":14})
        idata = analyzer.process()

        macd = idata["macd"]["analysis"]
        bbands = idata["bbands"]["analysis"]
        rsi = idata["rsi"]["analysis"]
        sma = idata["sma"]["analysis"]
        self.indicators = [macd,bbands,sma,rsi]

        self.signal = None

        #if bbands["slope"] > 1 and bbands["d"] > 35:
        if bbands["d"] > 35:
            if self.csdata["closed"][-1] < bbands["m"] and rsi["signal"] == "oversold" and bbands["trend"] == "bear":
            #if self.csdata["closed"][-2] > bbands["m"] and self.csdata["closed"][-1] < bbands["m"] and rsi["signal"] == "oversold":
                self.signal = "oversold"
            elif self.csdata["closed"][-1] > bbands["t"] and rsi["signal"] == "overbought":
                self.signal = "overbought"

        return self.set_results({
            "name": self.get_name(),
            "signal": self.signal,
            "last": self.csdata["closed"][-1],
            "time": time.strftime("%c")
            })
