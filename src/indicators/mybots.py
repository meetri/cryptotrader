import logging,time,uuid
from marketanalyzer import Analyzer
from trader import Trader
from coincalc import CoinCalc
from threading import Thread
from collections import OrderedDict

class BotMaster(object):


    def __init__(self):
        self.log = logging.getLogger('crypto')
        self.bag = {}
        self.executed_trades = []
        self.last_trade = 0
        self.min_trade_freq = 60
        self.max_trade_amount = 0.0001
        self.data = None
        self.botdata = {
                "bestbuy": {
                        "processing": {},
                        "history": []
                    }
                }



    def get_data(self):
        return self.data


    def set_data(self, data ):
        self.data = OrderedDict(data)


    def trade_executed(self):
        self.last_trade = time.time()
        self.log.info(self.last_trade)


    def bestBuyBotThread(self,trade,wallet):
        currency = trade["currency"]
        market = trade["market"]
        start_price = trade["details"]["price_entry"]
        trade_id = trade["trade_id"]

        trade_found = False
        while not trade_found:
            self.log.info("inside best buy bot")

            csdata = Trader(currency=currency).get_candlesticks("12h","30s")
            closed = csdata["closed"]

            score = 0
            for lbcnt in range(-3,-1):
                if closed[lbcnt] < closed[lbcnt-1]:
                    score += 2
                elif closed[lbcnt] == closed[lbcnt-1]:
                    score += 1

            if score <= 1:
                trade_found = True
                trade["original_price"] = trade["details"]["price_entry"]
                trade["price_entry"] = closed[-1]
                self.botdata["bestbuy"]["history"] += [trade]
                if trade_id in self.botdata["bestbuy"]["processing"]:
                    del self.botdata["bestbuy"]["processing"][trade_id]
                wallet.process_trade(trade)
            else:
                self.botdata["bestbuy"]["processing"][trade_id] = {
                        "tradeid": trade_id,
                        "price_entry": start_price,
                        "current_price": closed[-1],
                        "prev_price1": closed[-2],
                        "prev_price2": closed[-3],
                        "prev_price3": closed[-4],
                        "time": time.time(),
                        "score": score
                        }

                self.log.info("looking for better price {} -- {},{},{},{} -- score:{}".format(start_price,closed[-1],closed[-2],closed[-3],closed[-4],score))
                time.sleep(2)

        self.log.info("leaving best buy bot")


    def bestBuyBot(self, trade, wallet ):
        "this bot finds the best price for a trade"
        self.log.info("starting best buy bot")
        trade["trade_id"] = uuid.uuid4().hex
        thread = Thread(target = self.bestBuyBotThread, args = ( trade,wallet,))
        thread.start()


    def bandSurfer(self, currency ):
        "this bot initiates a trade"

        csdata = Trader(currency=currency).get_candlesticks("24h","5m")
        market = CoinCalc.getInstance().get_market(currency)
        analyzer = Analyzer( csdata )

        analyzer.add_indicator("macd",{})
        analyzer.add_indicator("bbands",{})
        analyzer.add_indicator("sma",{})
        idata = analyzer.process()

        macd = idata["macd"]["analysis"]
        bbands = idata["bbands"]["analysis"]
        sma = idata["sma"]["analysis"]

        #sma["signal"] = "oversold"

        mysignal = None
        price_entry = None
        if self.last_trade + self.min_trade_freq < time.time():
            #if sma["signal"] == "oversold":
            if ( bbands["signal"] == "oversold" and sma["signal"] == "oversold" ) or (macd["trend"] == "bull" and macd["trend_length"] <= 2 and bbands["signal"] == "oversold"):
            #if macd["trend"] == "bull" and macd["trend_length"] <= 2 and bbands["signal"] == "oversold":
                mysignal = "oversold"
                price_entry = csdata["closed"][-1]

            if macd["trend"] == "bull" and bbands["signal"] == "overbought":
                mysignal = "overbought"
        else:
            mysignal = "cooldown"

        self.set_data({
                "result": {
                    "details": {
                        "botname": "bandSurfer",
                        "last": csdata["closed"][-1],
                        "price_entry": price_entry,
                        "signal": mysignal,
                        "time":time.time()
                        },
                    "exchange": "bittrex",
                    "market": market,
                    "currency": currency,
                    "trade_amount": self.max_trade_amount,
                    "cs_time": csdata["time"][-1]
                    },
                "indicators": [macd,bbands,sma]
                })

        return self


    def middleBandSurfer(self, currency ):
        """
        this bot will first check the slope of the 50/sma and BBands middle band making sure it's in an incline,
        then it will check if a candle from above touces the center line. It will then execute a buy to best buy bot to trail the buy signal to it's bottom
        the sell middleBandSurferSell counterpart bot will profit is above margin and price touches the upper band. It will then go to best sell bot to trail
        the price higher for the ideal sell
        """

        csdata = Trader(currency=currency).get_candlesticks("24h","5m")
        market = CoinCalc.getInstance().get_market(currency)
        analyzer = Analyzer( csdata )

        analyzer.add_indicator("macd",{})
        analyzer.add_indicator("bbands",{})
        analyzer.add_indicator("sma",{})
        analyzer.add_indicator("rsi",{"overbought":70,"oversold":30,"period":14})
        idata = analyzer.process()

        macd = idata["macd"]["analysis"]
        bbands = idata["bbands"]["analysis"]
        rsi = idata["rsi"]["analysis"]
        sma = idata["sma"]["analysis"]

        mysignal = None
        price_entry = None
        if self.last_trade + self.min_trade_freq < time.time():

            #if bbands["slope"] > 1 and csdata["closed"][-1] < bbands["m"] and bbands["d"] > 35 and rsi["signal"] == "oversold":
            if csdata["closed"][-2] > bbands["m"] and csdata["closed"][-1] < bbands["m"] and bbands["d"] > 35 and rsi["signal"] == "oversold":
                mysignal = "oversold"
                price_entry = csdata["closed"][-1]
            #elif bbands["slope"] > 1 and csdata["closed"][-1] > bbands["t"] and bbands["d"] > 35 and rsi["signal"] == "overbought":
            elif csdata["closed"][-1] > bbands["t"] and bbands["d"] > 35 and rsi["signal"] == "overbought":
                mysignal = "overbought"
                price_exit = csdata["closed"][-1]

        else:
            mysignal = "cooldown"

        self.set_data({
                "result": {
                    "details": {
                        "botname": "middleBandSurfer",
                        "last": csdata["closed"][-1],
                        "price_entry": price_entry,
                        "signal": mysignal,
                        "time":time.time()
                        },
                    "exchange": "bittrex",
                    "market": market,
                    "currency": currency,
                    "trade_amount": self.max_trade_amount,
                    "cs_time": csdata["time"][-1]
                    },
                "indicators": [macd,bbands,sma,rsi]
                })

        return self
