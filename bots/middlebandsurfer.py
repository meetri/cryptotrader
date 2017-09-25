import os,sys,time
from basebot import BaseBot
from marketanalyzer import Analyzer
from exchange import Exchange

class MiddleBandSurfer(BaseBot):

    def __init__(self,market):
        BaseBot.__init__(self,market,"MiddleBandSurfer")
        self.trade_price_gap = 0.59


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
        analyzer.add_indicator("bbands",{"timeperiod":20,"nbdevup":1,"nbdevdn":1},label="bbands1")
        analyzer.add_indicator("sma",{"period":50})
        analyzer.add_indicator("rsi",{"overbought":63,"oversold":40,"period":14})
        analyzer.add_indicator("rsi",{"overbought":63,"oversold":40,"period":7},label="rsi2")
        idata = analyzer.process()
        self.track_signals ( idata )

        macd = idata["macd"]["analysis"]
        bbands = idata["bbands"]["analysis"]
        bbands1 = idata["bbands1"]["analysis"]
        rsi = idata["rsi"]["analysis"]
        rsi2 = idata["rsi2"]["analysis"]
        sma = idata["sma"]["analysis"]
        self.indicators = [macd,bbands,bbands1,sma,rsi,rsi2]

        self.signal = None

        debug = []
        #if bbands["slope"] > 1 and bbands["d"] > 35:
        if bbands["d"] > 25:
            debug += ["A:buy  when: l:{} < mb:{} & rsi = os/{} ( {} )".format(self.csdata["low"][-1],bbands["m"],rsi["signal"],rsi["rsi"])]
            debug += ["B:sell when: h:{} > tb:{} & rsi = ob/{} ( {} )".format(self.csdata["high"][-1],bbands["t"],rsi["signal"],rsi["rsi"])]
            debug += ["C:sell when: h:{} > mb:{} & rsi = ob/{} ( {} )".format(self.csdata["high"][-1],bbands["m"],rsi["signal"],rsi["rsi"])]
            if self.csdata["low"][-1] < bbands["m"] and rsi["signal"] == "oversold":
                self.signal = "oversold"
                debug += ["trigger buy rule A"]
            elif self.csdata["high"][-1] > bbands["t"] and rsi["signal"] == "overbought":
                self.signal = "overbought"
                debug += ["trigger sell rule B"]
            elif self.csdata["high"][-1] > bbands["m"] and rsi["signal"] == "overbought":
                self.signal = "overbought"
                debug += ["trigger sell rule C"]
        else:
            debug += ["bbands {} channel is too thin to trade in".format(bbands["d"])]

        self.debug = debug

        newsig = self.track_signals({ self.get_name(): { "analysis": { "signal" : self.signal } } })

        return self.set_results({
            "name": self.get_name(),
            "signal": self.signal,
            "cs": "5m",
            "last": self.csdata["closed"][-1],
            "high": self.csdata["high"][-1],
            "low": self.csdata["low"][-1],
            "time": time.strftime("%c")
            })
