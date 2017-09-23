import os,sys,talib,numpy,math,logging
from collections import OrderedDict

class RSI(object):

    def __init__(self,csdata, period = 14, overbought = 80, oversold = 20):

        self.log = logging.getLogger('crypto')
        #macd settings
        self.period = period
        self.overbought = overbought
        self.oversold = oversold
        #candlestick data
        self.csdata = csdata

        self.data = self.calc_value()


    def calc_value(self):
        if self.csdata is not None:
            try:
                self.data = talib.RSI(self.csdata["closed"], self.period )
            except Exception as ex:
                self.data = None

        return self.data


    def get_analysis(self ):
        if self.data is None:
            self.calc_value()

        rsi = self.data[-1]

        action = None
        if rsi >= self.overbought:
            action = "overbought"
        elif rsi <= self.oversold:
            action = "oversold"

        res = {
                "weight": 2,
                "time": self.csdata["time"][-1],
                "indicator-data": {
                    "rsi": rsi
                    },
                "analysis": OrderedDict()
                }

        res["analysis"]["name"] = "rsi"
        res["analysis"]["signal"] = action
        res["analysis"]["rsi"] = rsi

        return res
