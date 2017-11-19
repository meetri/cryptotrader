import os,sys,talib,numpy,logging
from influxdbwrapper import InfluxDbWrapper
from bittrex import Bittrex
from trader import Trader
from coincalc import CoinCalc
from macd import MACD
from bollingerbands import BBands

class HoldingMonitor(object):

    def __init__(self):

        self.log = logging.getLogger('crypto')
        #a list of all active investments
        self.holdings = []

        #a record of all active trades
        self.trades = []

        self.budget = 0

        #a list of indicators used validate trade positions
        self.indicators = ["macd","bbands"]

        #in memory data store for each market's analysis
        self.datastore = {}

        self.exchange = Bittrex()

        #candlestick chart data
        self.cs = None

        self.framesize = "5m"
        self.timeframe = "24h"

        self.settings = {
                "limit": 0.02,
                "profit": 0.03,
                "trailing_stop": 0.01
                }

    def setMarket(self,  market ):
        self.process(market)

    def setIndicators(self, indicators ):
        self.indicators = indicators


    def setTimeframe(self,timeframe, framesize ):
        self.timeframe = timeframe
        self.framesize = framesize

    def process(self, currency):
        if not currency in self.datastore:
            self.datastore[currency] = {}

        self.datastore[currency] = self.checkMarketStatus(currency)
        return self.datastore[currency]


    def checkMarkets(self, marketlist = None):

        if marketlist is None:
            marketlist = self.holdings

        for currency in marketlist:
            if not currency in self.datastore:
                self.datastore[currency] = {}

            self.datastore[currency] = self.checkMarketStatus(currency)

        return self.datastore

    def analyzeIndicators(self, currency, bot ):

        analysis = self.datastore[currency]
        market = CoinCalc.getInstance().get_market(currency)
        idata = []

        self.datastore[currency]["indicatordata"] = {}
        for indicator in analysis:
            if "analysis" in analysis[indicator]:
                self.log.info(analysis[indicator])
                res = analysis[indicator]["analysis"]
                idata += [res]
                self.datastore[currency]["indicatordata"][res["name"]] = analysis[indicator]

        botres = bot( self )
        action = botres["signal"]
        cur_price = botres["cur_price"]
        limitorder = botres["limitorder"]

        return {
                "market": market,
                "currency": currency,
                "cs_time": self.cs["time"][-1],
                "signal": action,
                "limitorder": limitorder,
                "indicators": idata
                }


    def checkMarketStatus(self, currency, data = None):
        if data is None:
            data = self.datastore[currency]

        market = CoinCalc.getInstance().get_market(currency)
        if market:
            traderTA = Trader(market)
            self.cs  = traderTA.get_candlesticks(self.timeframe,self.framesize)

            ath = 0
            for v in self.cs["high"]:
                if v > ath:
                    ath = v

            atl = 9999999
            for v in self.cs["low"]:
                if v < atl:
                    atl = v

            ret = {
                    "price" : {
                            "count": 0,
                            "last" : self.cs["closed"][-1],
                            "open": self.cs["open"][-1],
                            "HIGH": ath,
                            "LOW": atl,
                            "time": self.cs["time"][-1],
                        }
                    }
            for indicator in self.indicators:
                if indicator == "macd":
                    macd = MACD(self.cs)
                    ret["macd"] = macd.get_analysis(data)
                elif indicator == "bbands":
                    bb = BBands(self.cs,timeperiod=20,nbdevup=2, nbdevdn=2)
                    ret["bbands"] = bb.get_analysis(data)

            return ret

    def buyCurrency(self, indicatordata ):
        #self.log.info(indicatordata)
        currency = indicatordata["currency"]
        indicator_time = indicatordata["cs_time"]
        bid_price = indicatordata["limitorder"]
        amount = 0.1

        return self.xbuyCurrency( currency, indicator_time, bid_price, amount )

    def sellCurrency(self, indicatordata ):
        return {}

    def xbuyCurrency(self, currency, indicator_time, bid_price, amount ):

        for trade in self.trades:
            if trade["time"] == indicator_time and trade["currency"] == currency:
                return None

        market = CoinCalc.getInstance().get_market(currency)
        #TODO: grab this value dynamically
        trade_percent = 0.0025

        trade_cost = amount * bid_price * trade_percent
        break_even_price = trade_cost*2 + bid_price

        # for testing purposes...
        buy_price = bid_price
        limit = buy_price - (buy_price * self.settings["limit"] )
        exit = buy_price + ( buy_price * self.settings["profit"] )

        support = 0
        resistance = 0
        trailing_limit = 0

        buyMap = {
                "time": indicator_time,
                "currency": currency,
                "market": market,
                "desired_entry": bid_price,
                "real_entry": buy_price,
                "amount": amount,
                "trade_cost": trade_cost,
                "break_even_price": break_even_price,
                "desired_exit": exit,
                "real_exit": 0,
                "limit": limit,
                "trailing_limit": trailing_limit,
                "total_profit": 0
                }

        self.trades += [buyMap]
        return self.trades


    def analyzeTrade(self,trade):
        #buy_price = bid_price
        #limit = buy_price - (buy_price * self.settings["limit"] )
        #exit = buy_price + ( buy_price * self.settings["profit"] )

        cur_price = self.cs["closed"][-1]
        growth = ((cur_price - trade["real_entry"]) / cur_price) * 100

        trade["action"] = "hodl"
        trade["growth"] = round(growth,2)
        trade["profit"] = (cur_price * trade["amount"]) - ( trade["real_entry"] * trade["amount"] )
        #trade[""] = 0

        return trade

    # depends on a call to self.getMarkets() to have been made to get last price data
    def analyzeTrades(self):
        tradedata = []
        for trade in self.trades:
            tradedata += [ self.analyzeTrade(trade) ]
        return tradedata


    def getHoldings(self):
        holdings = {}
        calc = CoinCalc.getInstance()
        bal = self.exchange.account_get_balances().getData()
        if bal and bal["success"] == True:
            for currency in bal["result"]:
                if currency["Available"] > 0:
                    holdings[currency["Currency"]] = {
                            "Market": calc.get_market(currency["Currency"]),
                            "Balance": currency["Balance"],
                            "Available": currency["Available"],
                            "Pending": currency["Pending"]
                        }

        self.holdings = holdings
        return self.holdings



