import os,sys,talib,numpy,math,logging,numbers,time,datetime
from collections import OrderedDict

from baseindicator import BaseIndicator

class BBands(BaseIndicator):

    def __init__(self,csdata, config={}):

        config["charttypes"] = ["line","line","line"]

        BaseIndicator.__init__(self,csdata,config)

        self.timeperiod= config.get("timeperiod",5)
        self.nbdevup = config.get("nbdevup",2)
        self.nbdevdn = config.get("nbdevdn",2)
        self.matype = config.get("matype",0)
        self.label = config.get("label","bbands")

        self.chartcolors = config.get("chartcolors",["tomato","moccasin","limegreen"])
        self.chart_metric_keys = config.get("chartkeys",["{}-top".format(self.label),"{}-mid".format(self.label),"{}-low".format(self.label)])

        self.get_analysis()


    def width(self,index=1):
        return (self.top(index) - self.low(index)) / self.middle(index)

    def top(self,index=1):
        index = index * -1
        return self.data[0][index]

    def middle(self,index=1):
        index = index * -1
        return self.data[1][index]

    def low(self,index=1):
        index = index * -1
        return self.data[2][index]

    def get_settings(self):
        return "{}:{}:{}".format(self.timeperiod,self.nbdevup,self.nbdevdn)


    def getSlope(self, period = 14 ):
        slope = None
        for i in range(1,period+1):
            k = -1 * i
            if slope == None and self.data[1][k] != 0:
                slope = self.data[1][k-1] / self.data[1][k]
            elif self.data[1][k] != 0 and self.data[1][k-1] != 0:
                slope = slope / ( self.data[1][k-1] / self.data[1][k] )

        return slope


    def get_charts(self):

        allcharts = []
        label = ["top{}".format(self.label),"mid{}".format(self.label),"low{}".format(self.label)]
        color = self.chartcolors
        data = [[],[],[]]
        for i in range(0,len(self.csdata["closed"])):
            if isinstance(self.data[0][i],numbers.Number) and self.data[0][i] > 0:
                for j in range(0,3):
                    ts = time.mktime(datetime.datetime.strptime(self.csdata["time"][i], "%Y-%m-%dT%H:%M:%SZ").timetuple())
                    data[j].append({ "x": ts, "y": self.data[j][i] })

        for i in range(0,len(data)):
            chart = data[i]
            allcharts.append({
                "key": "{}".format(label[i]),
                "type": "line",
                "color": color[i],
                "yAxis": 1,
                "values": chart
                })

        return allcharts


    def get_bb(self):

        if self.csdata is not None:
            try:

                # bug in BBANDS doesn't work with small numbers... https://github.com/mrjbq7/ta-lib/issues/151
                sclosed = self.scaleup(self.csdata["closed"])
                #sclosed = self.csdata["closed"]

                data = talib.BBANDS( numpy.array(sclosed) , self.config["timeperiod"], self.config["nbdevup"], self.config["nbdevdn"], self.config.get("matype",0) )

                self.data = self.scaledown( data )

            except Exception as ex:
                self.data = None
                raise ex

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
        res["analysis"]["top"] = bbands["t"]
        res["analysis"]["mid"] = bbands["m"]
        res["analysis"]["low"] = bbands["l"]
        res["analysis"]["width"] = self.width()
        res["analysis"]["order"] = ["top","mid","low","width"]

        self.analysis = res
        return res

    def format_view(self):
        newres = dict(self.analysis["analysis"])
        newres["top"] = "{:.8f}".format(newres["top"])
        newres["mid"] = "{:.8f}".format(newres["mid"])
        newres["low"] = "{:.8f}".format(newres["low"])

        return newres
