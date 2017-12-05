import os,sys,talib,numpy,math,logging,time,datetime,math
from collections import OrderedDict
from baseindicator import BaseIndicator

class MACD(BaseIndicator):

    def __init__(self,csdata, config ):

        config["chartkeys"] = ["macd","signal","history"]
        config["chartcolors"] = ["blue","magenta","#555"]
        config["charttypes"] = ["line","line","column"]
        config["chartaxis"] = ["v1","v1","v2"]

        BaseIndicator.__init__(self,csdata,config)

        #macd settings
        self.fastperiod = config.get("fastperiod",12)
        self.slowperiod = config.get("slowperiod",26)
        self.signalperiod = config.get("signalperiod",9)

        #number of segments after bull trend does a buy action occur
        self.bull_lag = config.get("bull_lag",1)

        self.chart_scale = 2
        self.get_analysis()

    def mergeGraphConfig(self,metric,stockgraph):
        """used for amcharts"""
        stockgraph = BaseIndicator.mergeGraphConfig(self,metric,stockgraph)
        if metric == "history":
            stockgraph["negativeFillColors"] = "#db4c3c"
            stockgraph["useNegativeColorIfDown"] = True
            stockgraph["valueField"] = metric
            stockgraph["visibleInLegend"] = False
            stockgraph["fillColors"] = "limegreen"
            stockgraph["fillAlphas"] = 0.6
        return stockgraph

    def get_settings(self):
        return "{}:{}:{}".format(self.fastperiod,self.slowperiod,self.signalperiod)


    def get_macd(self):
        if self.csdata is not None:
            try:
                self.data = talib.MACD(self.csdata["closed"], self.fastperiod, self.slowperiod, self.signalperiod )
            except Exception as ex:
                self.data = None

        return self.data

    def getLast(self,index = 1):
        index = -1 * index
        return {
                "macd": self.data[0][index],
                "signal": self.data[1][index],
                "history": self.data[2][index],
                }

    def macd(self,index = 1):
        index = -1 * index
        return self.data[0][index]


    def signal(self,index = 1):
        index = -1 * index
        return self.data[1][index]


    def history(self,index = 1):
        index = -1 * index
        return self.data[2][index]


    def getTrend(self,ofs = 1):
        cur = self.getLast(ofs)
        if cur["history"] > 0:
            return "bull"
        else:
            return "bear"


    def getTrendLength(self):
        trend = self.getTrend()
        trendLength = 0
        for i in range(2,len(self.data[0])):
            if self.getTrend(i) != trend:
                return trendLength
            else:
                trendLength+=1

        return trendLength


    def get_analysis(self ):
        if self.data is None:
            self.get_macd()

        res = {
                "weight": 1,
                "indicator-data": {
                    "macd":self.macd(),
                    "signal": self.signal(),
                    "history": self.history()
                    },
                "analysis": OrderedDict()
                }

        res["analysis"]["name"] = "{}:{}".format(self.get_name(),self.get_settings())
        res["analysis"]["signal"] = None
        res["analysis"]["trend"] = self.getTrend()
        res["analysis"]["length"] = self.getTrendLength()
        res["analysis"]["macd"] = self.macd()
        res["analysis"]["sig"] =  self.signal()
        res["analysis"]["history"] = self.history()
        res["analysis"]["order"] = ["macd","sig","history","length"]

        self.analysis = res
        return res

    def format_view(self):
        newres = dict(self.analysis["analysis"])
        newres["macd"] = "{:.12f}".format(newres["macd"])
        newres["sig"] = "{:.12f}".format(newres["sig"])
        newres["history"] = "{:.12f}".format(newres["history"])

        return newres

