import os,sys,time
from basebot import BaseBot
from marketanalyzer import Analyzer
from exchange import Exchange

class BestSeller(BaseBot):

    def __init__(self,bot, trade, cs_size = "1m" ):
        BaseBot.__init__(self,bot.market,"BestSeller")
        self.trade_price_gap = bot.trade_price_gap
        self.trade_quantity = bot.trade_quantity
        self.minimum_trade_frequency = bot.minimum_trade_frequency
        self.max_ongoing_trades = bot.max_ongoing_trades
        self.counter = { "a":0, "b":0, "c":0, "d":0 }
        self.cs_size = cs_size
        self.active_trade = trade


    def process(self):
        BaseBot.process(self)

        self.csdata = self.trader.get_candlesticks("24h", self.cssize )
        analyzer = Analyzer( self.csdata )

        analyzer.add_indicator("bbands",{"timeperiod":20,"nbdevup":2,"nbdevdn":2})
        analyzer.add_indicator("bbands",{"timeperiod":20,"nbdevup":1,"nbdevdn":1},label="bbands1")
        idata = analyzer.process()
        self.track_signals ( idata )

        bbands = idata["bbands"]["analysis"]
        bbands1 = idata["bbands1"]["analysis"]
        self.indicators = [bbands,bbands1]

        self.trade_price = self.csdata["closed"][-1]

        self.signal = None

        debug = []

        if self.csdata["closed"][-2] < bbands["m"][-2]:
            self.signal = "sell"

        if self.csdata["high"][-1] > bbands["t"][-1]:
            pass
        elif self.csdata["closed"][-1] > self.csdata["m"][-1]
            pass
        elif self.csdata["low"][-1] > bbands["m"][-1]:
            pass

        self.debug = debug

        return self.set_results({
            "name": self.get_name(),
            "signal": self.signal,
            "cs": "5m",
            "last": self.csdata["closed"][-1],
            "high": self.csdata["high"][-1],
            "low": self.csdata["low"][-1],
            "time": time.strftime("%c")
            })
