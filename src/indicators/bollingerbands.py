import os,sys,talib,numpy,math,logging,numbers,time,datetime
from collections import OrderedDict

from baseindicator import BaseIndicator

class BBands(BaseIndicator):


    def __init__(self,csdata, timeperiod=5, nbdevup=2, nbdevdn=2, matype=0,label = "bbands"):

        BaseIndicator.__init__(self,csdata,label,{"timeperiod":timeperiod,"nbdevup":nbdevup,"nbdevdn":nbdevdn,"matype":matype})

        self.timeperiod= timeperiod
        self.nbdevup = nbdevup
        self.nbdevdn = nbdevdn
        self.matype = matype

        self.get_bb()

    def get_settings(self):
        return "{}:{}:{}".format(self.timeperiod,self.nbdevup,self.nbdevdn)


    def get_charts(self):
        allcharts = []
        label = ["top","middle","lower"]
        color = ["#7CFC00","#F0E68C","#F08080"]
        data = [[],[],[]]
        for i in range(0,len(self.csdata["closed"])):
            if isinstance(self.data[0][i],numbers.Number) and self.data[0][i] > 0:
                for j in range(0,2):
                    ts = time.mktime(datetime.datetime.strptime(self.csdata["time"][i], "%Y-%m-%dT%H:%M:%SZ").timetuple())
                    data[j].append({ "x": ts, "y": self.data[j][i] })

        for i in range(0,len(data)):
            chart = data[i]
            allcharts.append({
                "key": "{}:{}:{}:{}:{}".format(self.label,self.timeperiod,self.nbdevup,self.nbdevdn,label[i]),
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

                data = talib.BBANDS( numpy.array(sclosed) , self.config["timeperiod"], self.config["nbdevup"], self.config["nbdevdn"], self.config["matype"] )

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
        res["analysis"]["width"] = bbands["t"]-bbands["l"]
        res["analysis"]["order"] = ["top","mid","low"]

        self.analysis = res
        return res

    def format_view(self):
        newres = dict(self.analysis["analysis"])
        newres["top"] = "{:.8f}".format(newres["top"])
        newres["mid"] = "{:.8f}".format(newres["mid"])
        newres["low"] = "{:.8f}".format(newres["low"])

        return newres
