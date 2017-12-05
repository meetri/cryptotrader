import os,sys,talib,numpy,math,logging,time,datetime,numbers
from collections import OrderedDict

from baseindicator import BaseIndicator

class ATR(BaseIndicator):

    def __init__(self,csdata, config ):#period,label = "atr"):

        config["label"] = "{}{}".format(config.get("label","atr"),config["period"])
        config["period"] = config.get("period",30)
        config["chartaxis"] = ["v2"]
        config["chartcolors"] = config.get("chartcolors",["silver"])

        BaseIndicator.__init__(self,csdata,config)
        self.chart_scale = 1
        self.data = None
        self.analysis = None
        self.get_analysis()


    def last(self,index=1):
        index = index * -1
        return self.data[index]


    def get_settings(self):
        return self.config["period"]


    def get_atr(self):
        if self.csdata is not None:
            try:
                self.data = talib.ATR( numpy.array(self.csdata["high"]), numpy.array(self.csdata["low"]),numpy.array(self.csdata["closed"]),self.config["period"])
            except Exception as ex:
                print("Error: {}".format(ex))
                self.data = 0
                raise ex

        return self.data


    def format_view(self):
        newres = dict(self.analysis["analysis"])
        return newres


    def get_analysis(self):
        if self.data is None:
            self.get_atr()

        closing_time = self.csdata["time"][-1]
        atr = self.data[-1]
        signal = None

        self.analysis = {
                "analysis": {
                    "name": self.get_name(),
                    "signal": signal,
                    "atr": atr,
                    "order": ["atr"]
                    }
                }

        return self.analysis

