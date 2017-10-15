import os,sys,talib,numpy,math,logging
from collections import OrderedDict

class RSI(object):

    def __init__(self,csdata, period = 14, overbought = 80, oversold = 20, label = "rsi"):

        self.log = logging.getLogger('crypto')
        #macd settings
        self.period = period
        self.overbought = overbought
        self.oversold = oversold
        #candlestick data
        self.csdata = csdata
        self.label = label

        self.data = self.calc_value()

    def get_settings(self):
        return "{}:{}:{}".format(self.period,self.overbought,self.oversold)


    def get_name(self):
        return self.label


    def calc_value(self):
        if self.csdata is not None:
            try:
                self.data = talib.RSI(self.csdata["closed"], self.period )
            except Exception as ex:
                self.data = None

        return self.data


    def get_trend(self, rsi ):
        if rsi > 50:
            return "bull"
        elif rsi < 50:
            return "bear"
        else:
            return "even"


    def get_trend_length( self, offset = 0):
        rsi = self.data

        ofs = -1 * (offset+1)
        segments = 1

        trend = self.get_trend( rsi[ofs] )

        end = len(self.data) + ofs
        for i in range( end-1, 0, -1):
            if trend == self.get_trend( rsi[i] ):
                segments += 1
            else:
                break
        return {
                "trend": trend,
                "length": segments
                }


    def get_analysis(self ):
        if self.data is None:
            self.calc_value()

        rsi = self.data[-1]

        action = None
        if rsi >= self.overbought:
            action = "overbought"
        elif rsi <= self.oversold:
            action = "oversold"


        trendObj = self.get_trend_length()
        prev_trendObj = self.get_trend_length(trendObj["length"])


        res = {
                "weight": 2,
                "time": self.csdata["time"][-1],
                "indicator-data": {
                    "rsi": rsi
                    #"trend": trendObj["trend"],
                    #"trend_length": trendObj["length"]
                    },
                "analysis": OrderedDict()
                }

        res["analysis"]["name"] = "{}:{}".format(self.get_name(),self.get_settings())
        res["analysis"]["signal"] = action
        res["analysis"]["trend"] = trendObj["trend"]
        res["analysis"]["trendlength"] = trendObj["length"]
        res["analysis"]["prev_trend"] = prev_trendObj["trend"]
        res["analysis"]["prev_trendlength"] = prev_trendObj["length"]
        #res["analysis"]["debug"] = "{},{},{},{},{}".format(self.data[-1],self.data[-2],self.data[-3],self.data[-4],self.data[-5])
        res["analysis"]["rsi"] = rsi

        return res
