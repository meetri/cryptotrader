import os,sys,talib,numpy,math,logging,time,datetime,numbers
from collections import OrderedDict

from baseindicator import BaseIndicator

class ATR(BaseIndicator):

    def __init__(self,csdata, config ):#period,label = "atr"):
        BaseIndicator.__init__(self,csdata,config)
        self.data = None
        self.analysis = None
        self.get_analysis()



    def get_settings(self):
        return self.config["period"]

    def get_secondary_charts(self):
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
                "color": "#FFFFFF",
                "yAxis": 1,
                "values": data
                }]


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

    def get_chart_metric_colors(self,label):
        return "#999"

    def get_chart_metric_keys(self):
        return ["atr"]

    def get_chart_metrics(self,index = 0, scale = 0):
        if scale == 4 and numpy.isnan(self.data[index]):
            return {
                "atr": self.data[index],
            }

    def get_analysis(self):
        if self.data is None:
            self.get_atr()

        closing_time = self.csdata["time"][-1]
        atr = self.data[-1]
        signal = None

        self.analysis = {
                "weight": 2,
                "time": closing_time,
                "indicator-data": {
                    "atr": atr
                    },
                "analysis": {
                    "name": "{}".format(self.get_name()),
                    "signal": signal,
                    "atr": atr,
                    "order": ["atr"]
                    }
                }

        return self.analysis




