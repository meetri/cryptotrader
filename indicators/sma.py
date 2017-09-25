import os,sys,talib,numpy,math,logging
from collections import OrderedDict

class SMA(object):


    def __init__(self,csdata, period = 30,label = "sma"):

        self.log = logging.getLogger('crypto')
        #macd settings
        self.period = period
        #candlestick data
        self.csdata = csdata
        self.label = label

        self.data = self.get_sma()


    def get_settings(self):
        return "{}".format(self.period)


    def get_name(self):
        return self.label


    def get_sma(self):
        if self.csdata is not None:
            try:
                self.data = talib.SMA(self.csdata["closed"], self.period )
            except Exception as ex:
                self.data = None

        return self.data


    def get_analysis(self ):
        if self.data is None:
            self.get_sma()

        sma = self.data[-1]
        sma1 = self.data[-2]

        slope = None
        for k in range(-1,-10,-1):
            if slope == None:
                slope = self.data[k-1] / self.data[k]
            else:
                slope = slope / ( self.data[k-1] / self.data[k] )


        last_price = self.csdata["closed"][-1]
        closing_time = self.csdata["time"][-1]

        action = None
        if last_price < sma:
            action = "oversold"


        res = {
                "weight": 2,
                "time": closing_time,
                "indicator-data": {
                    "sma": sma
                    },
                "analysis": OrderedDict()
                }

        res["analysis"]["name"] = "{}:{}".format(self.get_name(),self.get_settings())
        res["analysis"]["signal"] = action
        res["analysis"]["sma"] = sma
        res["analysis"]["slope"] = slope

        return res

