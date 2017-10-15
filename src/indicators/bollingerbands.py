import os,sys,talib,numpy,math,logging
from collections import OrderedDict

class BBands(object):


    def __init__(self,csdata, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0,label = "bbands"):
        self.log = logging.getLogger('crypto')

        self.timeperiod= timeperiod
        self.nbdevup = nbdevup
        self.nbdevdn = nbdevdn
        self.matype = matype

        self.label = label

        #candlestick data
        self.csdata = csdata
        self.get_bb()

    def get_settings(self):
        return "{}:{}:{}".format(self.timeperiod,self.nbdevup,self.nbdevdn)


    def get_name(self):
        return self.label

    def get_bb(self):

        if self.csdata is not None:
            try:
                self.data = talib.BBANDS(self.csdata["closed"], self.timeperiod, self.nbdevup, self.nbdevdn, self.matype )
                #self.log.info(self.data)
            except Exception as ex:
                self.data = None

        return self.data


    def get_analysis(self):
        if self.data is None:
            self.get_bb()

        bbands = {
                "t":self.data[0][-1],
                "m":self.data[1][-1],
                "l":self.data[2][-1],
                }

        height = bbands["t"] - bbands["l"]

        last_price = self.csdata["closed"][-1]
        closing_time = self.csdata["time"][-1]

        slope = None
        for k in range(-1,-5,-1):
            if slope == None:
                slope = self.data[1][k-1] / self.data[1][k]
            else:
                slope = slope / ( self.data[1][k-1] / self.data[1][k] )

        signal = None
        target_price = None
        if last_price > bbands["t"]:
            signal = "overbought"
            target_price = bbands["l"]

        if last_price < bbands["l"]:
            signal = "oversold"
            target_price = bbands["t"]

        trend = None
        if last_price > bbands["m"]:
            trend = "bull"

        if last_price < bbands["m"]:
            trend = "bear"

        res = {
                "weight": 2,
                "time": closing_time,
                "indicator-data": {
                    "top": bbands["t"],
                    "middle": bbands["m"],
                    "lower": bbands["l"],
                    },
                "analysis": OrderedDict()
                }

        res["analysis"]["name"] = "{}:{}".format(self.get_name(),self.get_settings())
        res["analysis"]["signal"] = signal
        res["analysis"]["trend"] = trend
        res["analysis"]["slope"] = slope
        res["analysis"]["t"] = bbands["t"]
        res["analysis"]["m"] = bbands["m"]
        res["analysis"]["l"] = bbands["l"]
        res["analysis"]["d"] = bbands["t"]-bbands["l"]

        return res

