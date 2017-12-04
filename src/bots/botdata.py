import json,time,datetime,logging
from order import Order
from tools import Tools

class BotDataProvider(object):

    def __init__(self,bot):
        self.bot = bot
        self.log = logging.getLogger('crypto')
        self.chartsize = 0

    def get_amchart_panels(self):

        fieldkeys = {}
        fieldmappings = []
        fieldmappings.append({"fromField":"open","toField":"open"})
        fieldmappings.append({"fromField":"high","toField":"high"})
        fieldmappings.append({"fromField":"low","toField":"low"})
        fieldmappings.append({"fromField":"close","toField":"close"})
        fieldmappings.append({"fromField":"volume","toField":"volume"})

        stockgraphkeys = {}
        stockgraphs = []

        stockgraphs.append({
            "title": self.bot.getMarket(),
            "type": "candlestick",
            "id": "g1",
            "openField": "open",
            "closeField": "close",
            "highField": "high",
            "lowField": "low",
            "valueField": "close",
            "lineColor": "#7f8da9",
            "fillColors": "#7f8da9",
            "negativeLineColor": "#db4c3c",
            "negativeFillColors": "#db4c3c",
            "fillAlphas": 1,
            #"comparedGraphLineThickness": 2,
            #"columnWidth": 0.7,
            "useDataSetColors": False,
            "comparable": True,
            "compareField": "close",
            "showBalloon": False,
            "proCandlesticks": True
        })

        for indicator in self.bot.analyzer.getIndicators():
            metrics = indicator["object"].get_chart_metric_keys()
            for metric in metrics:
                if indicator["object"].get_chart_scale() == 1:
                    label = indicator["object"].label
                    if metric not in stockgraphkeys:
                        stockgraphkeys[metric] = 1
                        stockgraphs.append({
                            "title": metric,
                            "lineColor": indicator["object"].get_chart_metric_colors(metric),
                            "lineThickness": 1,
                            "valueField": metric,
                            "useDataSetColors": False
                        })

        chart_corrected = 0
        amchart = []
        for i in range(0,len(self.bot.csdata["time"])):
            ts = time.mktime(datetime.datetime.strptime(self.bot.csdata["time"][i], "%Y-%m-%dT%H:%M:%SZ").timetuple())*1000
            if self.bot.csdata["open"][i] > 0:
                datafields = {
                    "date": ts,
                    "open": self.bot.csdata["open"][i],
                    "close": self.bot.csdata["closed"][i],
                    "high": self.bot.csdata["high"][i],
                    "low": self.bot.csdata["low"][i],
                    "volume": self.bot.csdata["volume"][i] - self.bot.csdata["basevolume"][i]
                }
                for indicator in self.bot.analyzer.getIndicators():
                    if "object" in indicator:
                        v = indicator["object"].get_chart_metrics(i,1)
                        if v:
                            datafields = {**datafields, **v}
                            for key in v:
                                if key not in fieldkeys:
                                    fieldkeys[key] = 1
                                    fieldmappings.append({"fromField":key,"toField":key})

                amchart.append(datafields)
            else:
                chart_corrected += 1

        datasets = [{
            "title": self.bot.getMarket(),
            "fieldMappings": fieldmappings,
            "categoryField": "date",
            "color": "#7f8da9",
            "dataProvider": amchart,
        }]

        return [{ "errors": chart_corrected,"datasets":datasets,"stockgraphs":stockgraphs}]




    def get_tacharts(self):
        allcharts = []
        secondarycharts = []
        tertiarycharts = []

        for i in self.bot.analyzer.getIndicators():
            chart = i["object"].get_charts()
            for chart in i["object"].get_charts():
                if chart is not None:
                    chart["values"] = chart["values"][self.chartsize:]
                    allcharts.append(chart)
            for chart in i["object"].get_secondary_charts():
                if chart is not None:
                    chart["values"] = chart["values"][self.chartsize:]
                    secondarycharts.append(chart)
            for chart in i["object"].get_tertiary_charts():
                if chart is not None:
                    chart["values"] = chart["values"][self.chartsize:]
                    tertiarycharts.append(chart)


        signalPoints = {"buy":[],"sell":[]}
        for signal in self.bot.all_signals:
            if signal["signal"] in ["buy","sell"]:
                ts = time.mktime(datetime.datetime.strptime(signal["cstime"], "%Y-%m-%dT%H:%M:%SZ").timetuple())
                signalPoints[signal["signal"]].append({ "x": ts, "y": signal["rate"],"size": 15,})

        allcharts.append({"key": "sell", "type": "scatter", "yAxis": 1, "values": signalPoints["sell"]})
        allcharts.append({"key": "buy", "type": "scatter", "yAxis": 1, "values": signalPoints["buy"]})

        pricechart = { "color":"#6BF","key": "Price", "type": "line", "yAxis": 1, "values": [] }
        for i in range(0,len(self.bot.csdata["closed"])):
            if len(self.bot.csdata["time"]) > i:
                ts = time.mktime(datetime.datetime.strptime(self.bot.csdata["time"][i], "%Y-%m-%dT%H:%M:%SZ").timetuple())
                if self.bot.csdata["closed"][i] > 0:
                    pricechart["values"].append({
                        "x": ts,
                        "y": self.bot.csdata["closed"][i]
                    })
            else:
                self.log.error("TACharts: missing time data index: {} time data length: {}".format(i,len(self.bot.csdata["time"])))

        pricechart["values"] = pricechart["values"][self.chartsize:]
        allcharts.append(pricechart)

        return {
                "primary": allcharts,
                "secondary": secondarycharts,
                "tertiary": tertiarycharts
                }


    def get_chart(self):
        fullchart = []
        chart_corrected = 0
        for i in range(0,len(self.bot.csdata["open"])):
            if len(self.bot.csdata["time"]) > i:
                ts = time.mktime(datetime.datetime.strptime(self.bot.csdata["time"][i], "%Y-%m-%dT%H:%M:%SZ").timetuple())
                if self.bot.csdata["open"][i] > 0:
                    fullchart.append({
                        "date": ts,
                        "open": self.bot.csdata["open"][i],
                        "close": self.bot.csdata["closed"][i],
                        "high": self.bot.csdata["high"][i],
                        "low": self.bot.csdata["low"][i],
                        "volume": self.bot.csdata["volume"][i]
                        })
                else:
                    chart_corrected += 1
            else:
                self.log.error("getChart: missing time data index: {} time data length: {}".format(i,len(self.bot.csdata["time"])))

        return [{ "errors": chart_corrected,"values" : fullchart }]


    def get_trades(self):
        # use ordermanager to get trades associated with this bot...
        om = self.bot.getOrderManager()

        trades = []
        for trade in om.getBotOrders():
            trades.append(trade.getView(self.bot.csdata["closed"][-1]))

        return {
                "trades": trades
                }


    def getInfo(self, query = None ):
        result = None
        if query == "chart":
            result = self.get_chart()
        elif query == "tacharts":
            result = self.get_tacharts()
        elif query == "trades":
            result = self.get_trades()
        elif query == "amcharts":
            result =  self.get_amchart_panels()
        else:
            indicators = []
            for i in self.bot.analyzer.getIndicators():
                if i["object"]:
                    indicators.append(i["object"].format_view())

            result = {
                "bot": self.bot.info(),
                "indicators": indicators,
                "signals": self.bot.signal_history,
                "signal_history": self.bot.all_signals,
                "debug" : self.bot.debug
                }

            if self.bot.backtest:
                result["backtest"] = {
                        "startprice" : self.bot.backtest_startprice,
                        "endprice": self.bot.backtest_endprice,
                        "change": "{:.2f}".format(Tools.calculateGrowth(self.bot.backtest_endprice,self.bot.backtest_startprice))
                        }

        return json.dumps(result)



    #TODO move this out into some type of data provider ...
    def xget_info(self, data = None):

        if data == "chart":
            return self.get_chart()
        elif data == "tacharts":
            return self.get_tacharts()
        elif data == "trades":
            return self.get_trades()
        elif data == "amcharts":
            return self.get_amchart_panels()
        else:

            indicators = []
            for i in self.indicators:
                indicators.append(i["object"].format_view())

            botinfo = dict(self.results)
            botinfo["name"] = self.name
            botinfo["market"] = self.market
            botinfo["min_trade_freq"] = self.minimum_trade_frequency
            botinfo["max_active_trades"] = self.max_ongoing_trades
            botinfo["max_trade_quantity"] = self.trade_quantity

            return json.dumps({
                "bot": botinfo,
                "indicators": indicators,
                "debug" : self.debug
                })
