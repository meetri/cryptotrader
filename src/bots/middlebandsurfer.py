import os,sys,time
from basebot import BaseBot
from marketanalyzer import Analyzer
from exchange import Exchange

class MiddleBandSurfer(BaseBot):

    def __init__(self,market, trade_price_gap, max_trade_qty = 0.01, min_trade_freq = 120, max_trades = 10):
        BaseBot.__init__(self,market,"MiddleBandSurfer")
        self.trade_price_gap = trade_price_gap
        self.trade_quantity = max_trade_qty
        self.minimum_trade_frequency = min_trade_freq
        self.max_ongoing_trades = max_trades
        self.counter = { "a":0, "b":0, "c":0, "d":0 }


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
        analyzer.add_indicator("bbands",{"timeperiod":20,"nbdevup":2,"nbdevdn":2})
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
        #self.indicators = [macd,bbands,bbands1,sma,rsi,rsi2]
        self.indicators = analyzer.get_indicators()

        self.signal = None

        debug = []
        #if bbands["slope"] > 1 and bbands["d"] > 35:
        #if bbands["width"] > 25:
        if True:
            debug += ["A[{}]:buy  when: l:{} < mb:{} & rsi = os/{} ( {} )".format(self.counter["a"],self.csdata["low"][-1],bbands["mid"],rsi["signal"],rsi["rsi"])]
            debug += ["B[{}]:sell when: c:{} > tb:{} & rsi = os/{} ( {} )".format(self.counter["b"],self.csdata["closed"][-1],bbands["top"],rsi["signal"],rsi["rsi"])]
            debug += ["C[{}]:sell when: h:{} > tb:{} & rsi = ob/{} ( {} )".format(self.counter["c"],self.csdata["high"][-1],bbands["top"],rsi["signal"],rsi["rsi"])]
            debug += ["D[{}]:sell when: h:{} > mb:{} & rsi = ob/{} ( {} )".format(self.counter["d"],self.csdata["high"][-1],bbands["mid"],rsi["signal"],rsi["rsi"])]
            if self.csdata["low"][-1] < bbands["mid"] and rsi["signal"] == "oversold":
                self.counter["a"] += 1
                self.signal = "oversold"
                debug += ["trigger buy rule A"]
            elif self.csdata["closed"][-1] > bbands["top"] and rsi["signal"] == "overbought":
                self.counter["b"] += 1
                self.signal = "overbought"
                self.order_type = "trailing"
                debug += ["trigger sell rule B using trailing algo"]
            elif self.csdata["high"][-1] > bbands["top"] and rsi["signal"] == "overbought":
                self.counter["c"] += 1
                self.signal = "overbought"
                debug += ["trigger sell rule C"]
            elif self.csdata["high"][-1] > bbands["mid"] and rsi["signal"] == "overbought":
                self.counter["d"] += 1
                self.signal = "overbought"
                debug += ["trigger sell rule D"]
        else:
            debug += ["bbands {} channel is too thin to trade in".format(bbands["width"])]

        self.debug = debug

        newsig = self.track_signals({ self.get_name(): { "analysis": { "signal" : self.signal } } })

        return self.set_results({
            "name": self.get_name(),
            "signal": self.signal,
            "cs": "5m",
            "last": self.csdata["closed"][-1],
            "high": self.csdata["high"][-1],
            "low": self.csdata["low"][-1],
            "time": time.strftime("%c"),
            "order": ["time","name","signal","cs","last","high","low"]
            })
