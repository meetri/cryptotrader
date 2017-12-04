import os,sys,talib,numpy,math,logging,numbers,time,datetime
from collections import OrderedDict

class RSI(object):

    def __init__(self,csdata,config = {}):

        self.config = config
        self.log = logging.getLogger('crypto')
        #macd setting
        self.period = config.get("period",14)
        self.overbought = config.get("overbought",80)
        self.oversold = config.get("oversold",20)
        #candlestick data
        self.csdata = csdata
        self.label = config.get("label","rsi")
        self.analysis = None

        self.chartcolors = config.get("chartcolors",["#FFF"])
        self.chart_metric_keys = config.get("chartkeys",[self.label])

        self.data = self.calc_value()
        self.get_analysis()
        self.chart_scale = 1

    def last(self,index=1):
        index = index * -1
        return self.data[index]

    def isOverbought(self,index = 1):
        index = index * -1
        if self.data[index] >= self.overbought:
            return (self.data[index]-self.overbought)
        else:
            return None


    def isOversold(self,index = 1):
        index = index * -1
        if self.data[index] <= self.oversold:
            return (self.oversold-self.data[index])
        else:
            return None


    def get_data(self):
        return data

    def get_charts(self):
        return []

    def get_tertiary_charts(self):
        return []

    def get_secondary_charts(self):
        data = []
        start_ts = None
        end_ts = None
        for i in range(0,len(self.csdata["closed"])):
            if isinstance(self.data[i],numbers.Number) and self.data[i] > 0:
                ts = time.mktime(datetime.datetime.strptime(self.csdata["time"][i], "%Y-%m-%dT%H:%M:%SZ").timetuple())

                data.append({
                    "x": ts,
                    "y": self.data[i],
                    })

        start_ts = time.mktime(datetime.datetime.strptime(self.csdata["time"][0], "%Y-%m-%dT%H:%M:%SZ").timetuple())
        end_ts = time.mktime(datetime.datetime.strptime(self.csdata["time"][-1], "%Y-%m-%dT%H:%M:%SZ").timetuple())
        return [{
                "key": "overbought",
                "type": "line",
                "color": "#990000",
                "yAxis": 2,
                "values": [{"x":start_ts,"y":self.overbought},{"x":end_ts,"y":self.overbought}]
                },{
                "key": "oversold",
                "type": "line",
                "color": "#009900",
                "yAxis": 2,
                "values": [{"x":start_ts,"y":self.oversold},{"x":end_ts,"y":self.oversold}]
                },{
                "key": "{}:{}".format(self.label,self.period),
                "type": "line",
                "color": "#555555",
                "yAxis": 2,
                "values": data
                }]


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


    def get_trend(self, rsi ):
        if rsi > 50:
            return "bull"
        elif rsi < 50:
            return "bear"
        else:
            return "even"


    def get_trend_length( self, offset = 0):
        rsi = self.data

        ofs = -1 * (offset+1)
        segments = 1

        trend = self.get_trend( rsi[ofs] )

        end = len(self.data) + ofs
        for i in range( end-1, 0, -1):
            if trend == self.get_trend( rsi[i] ):
                segments += 1
            else:
                break
        return {
                "trend": trend,
                "length": segments
                }


    def get_analysis(self ):
        if self.data is None:
            self.calc_value()

        rsi = self.data[-1]

        action = None
        if rsi >= self.overbought:
            action = "overbought"
        elif rsi <= self.oversold:
            action = "oversold"


        trendObj = self.get_trend_length()
        prev_trendObj = self.get_trend_length(trendObj["length"])


        res = {
                "weight": 2,
                "time": self.csdata["time"][-1],
                "indicator-data": {
                    "rsi": rsi
                    #"trend": trendObj["trend"],
                    #"trend_length": trendObj["length"]
                    },
                "analysis": OrderedDict()
                }

        res["analysis"]["name"] = "{}:{}".format(self.get_name(),self.get_settings())
        res["analysis"]["signal"] = action
        res["analysis"]["trend"] = trendObj["trend"]
        res["analysis"]["trendlength"] = trendObj["length"]
        res["analysis"]["prev_trend"] = prev_trendObj["trend"]
        res["analysis"]["prev_trendlength"] = prev_trendObj["length"]
        #res["analysis"]["debug"] = "{},{},{},{},{}".format(self.data[-1],self.data[-2],self.data[-3],self.data[-4],self.data[-5])
        res["analysis"]["rsi"] = rsi
        res["analysis"]["order"] = ["rsi"]

        self.analysis = res
        return res

    def get_chart_metric_colors(self,label):
        return "#999"

    def get_chart_scale(self):
        return self.chart_scale

    def get_chart_metric_keys(self):
        return self.chart_metric_keys


    def get_chart_metrics(self,index = 0, scale = 0):
            if not numpy.isnan(self.data[index]):
                return {
                    "rsi": self.data[index],
                }

    def format_view(self):
        newres = dict(self.analysis["analysis"])
        newres["rsi"] = "{:.2f}".format(newres["rsi"])
        return newres
