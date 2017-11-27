import os,sys,talib,numpy,math,logging,time,datetime,numbers
from collections import OrderedDict

from baseindicator import BaseIndicator

class ATR(BaseIndicator):

    def __init__(self,csdata,period,label = "atr"):
        BaseIndicator.__init__(self,csdata,label,{"period":period})


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
                self.data = None
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




