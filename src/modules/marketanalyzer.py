import os,sys,talib,numpy,logging
from collections import OrderedDict
from influxdbwrapper import InfluxDbWrapper
from bittrex import Bittrex
from trader import Trader
from coincalc import CoinCalc
from macd import MACD
from bollingerbands import BBands
from sma import SMA
from rsi import RSI

class Analyzer(object):

    def __init__(self, csdata ):
        self.log = logging.getLogger('crypto')

        #a list of indicators used validate trade positions
        self.indicators = []

        #in memory data store for each market's analysis
        self.datastore = {}

        #candlestick chart data
        self.cs = csdata

        self.options = {}


    def add_indicator(self, indicator, options = {}, label = None ):
        if label is None:
            label = indicator
        self.indicators += [{"indicator":indicator,"label":label,"options":options}]


    def process(self):
        ath = 0
        for v in self.cs["high"]:
            if v > ath:
                ath = v

        atl = 9999999
        for v in self.cs["low"]:
            if v < atl:
                atl = v

        """
        ret = OrderedDict({
                "price" : {
                        "count": 0,
                        "last" : self.cs["closed"][-1],
                        "open": self.cs["open"][-1],
                        "HIGH": ath,
                        "LOW": atl,
                        "time": self.cs["time"][-1],
                    }
                })#
        """

        ret ={}

        for indicatorObj in self.indicators:
            indicator = indicatorObj.get("indicator")
            label = indicatorObj.get("label")
            options = indicatorObj.get("options",{})

            if label is None or len(label) == 0:
                label = indicator

            if indicator == "macd":
                macd = MACD(self.cs)
                ret[label] = macd.get_macd_analysis()
            elif indicator == "bbands":
                bb = BBands(self.cs,**options)
                ret[label] = bb.get_analysis()
            elif indicator == "sma":
                sma = SMA(self.cs,**options)
                ret[label] = sma.get_analysis()
            elif indicator == "rsi":
                rsi = RSI(self.cs,**options)
                ret[label] = rsi.get_analysis()

        return ret
