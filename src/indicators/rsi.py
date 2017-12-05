import os,sys,talib,numpy,math,logging,numbers,time,datetime
from collections import OrderedDict

from baseindicator import BaseIndicator

class RSI(BaseIndicator):

    def __init__(self,csdata,config = {}):

        config["label"] = config.get("label","sma")
        config["period"] = config.get("period",30)
        config["label"] = "{}{}".format(config["label"],config["period"])
        config["chartcolors"] = config.get("chartcolors",["fuchsia"])

        BaseIndicator.__init__(self,csdata,config)
        self.chart_scale = 1

        self.period = config.get("period",14)
        self.overbought = config.get("overbought",80)
        self.oversold = config.get("oversold",20)

        self.get_analysis()


    def last(self,index=1):
        index = index * -1
        return self.data[index]


    def isOverbought(self,index = 1):
        index = index * -1
        if self.data[index] >= self.overbought:
            return (self.data[index]-self.overbought)
        else:
            return False


    def isOversold(self,index = 1):
        index = index * -1
        if self.data[index] <= self.oversold:
            return (self.oversold-self.data[index])
        else:
            return False

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


    def getTrend(self, rsi ):
        if rsi > 50:
            return "bull"
        elif rsi < 50:
            return "bear"
        else:
            return "even"


    def get_analysis(self ):
        if self.data is None:
            self.calc_value()

        rsi = self.data[-1]

        action = None
        if self.isOverbought():
            action = "overbought"
        elif self.isOversold():
            action = "oversold"

        res = { "analysis": {} }

        res["analysis"]["name"] = self.get_name()
        res["analysis"]["signal"] = action
        res["analysis"]["rsi"] = rsi
        res["analysis"]["order"] = ["rsi"]

        self.analysis = res

        return res


    def format_view(self):
        newres = dict(self.analysis["analysis"])
        newres["rsi"] = "{:.2f}".format(newres["rsi"])
        return newres
