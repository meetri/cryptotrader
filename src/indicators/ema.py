import os,sys,talib,numpy,math,logging,time,datetime,numbers
from collections import OrderedDict

from baseindicator import BaseIndicator

class EMA(BaseIndicator):


    def __init__(self,csdata, config = {}):

        config["period"] = config.get("period",30)
        config["label"] = config.get("label","ema")
        config["label"] = "{}{}".format(config["label"],config["period"])

        BaseIndicator.__init__(self,csdata,config)

        self.chartcolors = ["mediumslateblue"]

        self.data = None
        self.analysis = None
        self.get_analysis()


    def get_settings(self):
        return "{}".format(self.config["period"])


    def get_charts(self):
        data = []
        for i in range(0,len(self.csdata["closed"])):
            if isinstance(self.data[i],numbers.Number) and self.data[i] > 0:
                ts = time.mktime(datetime.datetime.strptime(self.csdata["time"][i], "%Y-%m-%dT%H:%M:%SZ").timetuple())
                data.append({
                    "x": ts,
                    "y": self.data[i],
                    })

        return [{
                "key": "{}:{}".format(self.label,self.config["period"]),
                "type": "line",
                "color": "#FFF5EE",
                "yAxis": 1,
                "values": data
                }]


    def get_ema(self):
        if self.csdata is not None:
            try:
                sclosed = self.scaleup( self.csdata["closed"])
                data = talib.EMA( numpy.array(sclosed), self.config["period"])
                self.data = self.scaledown(data)
                # scaledown
            except Exception as ex:
                self.data = None
                raise ex

        return self.data


    def get_analysis(self ):
        if self.data is None:
            self.get_ema()

        ema = self.data[-1]
        ema1 = self.data[-2]

        slope = None
        for k in range(-1,-10,-1):
            if slope == None:
                slope = self.data[k-1] / self.data[k]
            else:
                slope = slope / ( self.data[k-1] / self.data[k] )


        last_price = self.csdata["closed"][-1]
        closing_time = self.csdata["time"][-1]

        action = None
        if last_price < ema:
            action = "oversold"


        res = {
                "weight": 2,
                "time": closing_time,
                "indicator-data": {
                    "ema": ema
                    },
                "analysis": OrderedDict()
                }

        res["analysis"]["name"] = "{}:{}".format(self.get_name(),self.get_settings())
        res["analysis"]["signal"] = action
        res["analysis"]["ema"] = ema
        res["analysis"]["slope"] = slope
        res["analysis"]["order"] = ["ema"]

        self.analysis = res
        return res

    def format_view(self):
        newres = dict(self.analysis["analysis"])
        newres["slope"] = "{:.4f}".format(newres["slope"])
        newres["ema"] = "{:.8f}".format(newres["ema"])

        return newres

