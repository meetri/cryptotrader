import os,sys,talib,numpy,math,logging,time,datetime,math
from collections import OrderedDict

class MACD(object):


    def __init__(self,csdata, config ): #fastperiod=12, slowperiod=26, signalperiod=9 , bull_lag = 1):

        #macd settings
        self.fastperiod = config.get("fastperiod",12)
        self.slowperiod = config.get("slowperiod",26)
        self.signalperiod = config.get("signalperiod",9)
        self.label = config.get("label","macd")

        #number of segments after bull trend does a buy action occur
        self.bull_lag = config.get("bull_lag",1)

        #candlestick data
        self.csdata = csdata

        self.data = self.get_macd()
        self.analysis = None


    def get_tertiary_charts(self):

        macddata = []
        signaldata = []
        historydata = []

        for i in range(0,len(self.csdata["closed"])):
            if not math.isnan(self.data[0][i]) and not math.isnan(self.data[1][i]) and not math.isnan(self.data[2][i]):
                ts = time.mktime(datetime.datetime.strptime(self.csdata["time"][i], "%Y-%m-%dT%H:%M:%SZ").timetuple())

                macddata.append({ "x": ts, "y": self.data[0][i], })
                signaldata.append({ "x": ts, "y": self.data[1][i], })
                historydata.append({ "x": ts, "y": self.data[2][i], })


        return [{
                "key": "macd",
                "type": "line",
                "color": "#990000",
                "yAxis": 1,
                "values": macddata
                },{
                "key": "signal",
                "type": "line",
                "color": "#009900",
                "yAxis": 1,
                "values": signaldata
                },{
                "key": "history",
                "type": "bar",
                "color": "#555555",
                "yAxis": 2,
                "values": historydata
                }]

    def get_secondary_charts(self):
        return []

    def get_secondary_charts(self):
        return []


    def get_settings(self):
        return "{}:{}:{}".format(self.fastperiod,self.slowperiod,self.signalperiod)


    def get_name(self):
        return self.label

    def get_charts(self):
        return []

    def get_macd(self):
        if self.csdata is not None:
            try:
                self.data = talib.MACD(self.csdata["closed"], self.fastperiod, self.slowperiod, self.signalperiod )
            except Exception as ex:
                self.data = None

        return self.data


    def get_trend(self, history ):
        if history > 0:
            return "bull"
        elif history < 0:
            return "bear"
        else:
            return "even"

    def get_trend_length( self, offset = 0 ):
        macd_history = self.data[2]

        end = len(macd_history) - ( 1 + offset )
        segments = 1

        trend = self.get_trend(macd_history[end])
        for i in range( end-1, 0, -1):
            if trend == self.get_trend( macd_history[i] ):
                segments += 1
            else:
                break
        return {
                "trend": trend,
                "length": segments
                }


    def get_analysis(self ):
        if self.data is None:
            self.get_macd()

        macd_all = self.data
        macd = {
                "macd":macd_all[0][-1],
                "signal":macd_all[1][-1],
                "history":macd_all[2][-1],
                }

        tdata = self.get_trend_length()

        action = None
        if tdata["trend"] == "bull" and tdata["length"] == self.bull_lag:
            action = "buy"


        last_price = self.csdata["closed"][-1]
        last_frame_price = self.csdata["closed"][-2]

        closing_time = self.csdata["time"][-1]

        strength = math.fabs(macd_all[2][-2] - macd_all[2][-1])

        ath = 0;
        atl = 99999999;
        for v in macd_all[2]:
            if v > ath:
                ath = v
            if v < atl:
                atl = v

        res = {
                "weight": 1,
                "time": closing_time,
                "indicator-data": {
                    "macd":macd_all[0][-1],
                    "signal":macd_all[1][-1],
                    "history":macd_all[2][-1],
                    "ath": ath,
                    "atl": atl,
                    "strength": strength
                    },
                "analysis": OrderedDict()
                }

        res["analysis"]["name"] = "{}:{}".format(self.get_name(),self.get_settings())
        res["analysis"]["signal"] = action
        res["analysis"]["trend"] = tdata["trend"]
        res["analysis"]["trendlength"] = tdata["length"]
        res["analysis"]["macd"] = macd_all[0][-1]
        res["analysis"]["sig"] = macd_all[1][-1]
        res["analysis"]["history"] = macd_all[2][-1]
        res["analysis"]["order"] = ["macd","sig","history"]

        self.analysis = res
        return res

    def format_view(self):
        newres = dict(self.analysis["analysis"])
        newres["macd"] = "{:.12f}".format(newres["macd"])
        newres["sig"] = "{:.12f}".format(newres["sig"])
        newres["history"] = "{:.12f}".format(newres["history"])

        return newres

