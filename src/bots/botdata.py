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
        stockgraphs = [[],[],[]]

        stockgraphs[0].append({
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
                scale = indicator["object"].get_chart_scale()
                label = indicator["object"].label
                if metric not in stockgraphkeys:
                    stockgraphkeys[metric] = 1
                    sg = {
                        "title": metric,
                        "lineThickness": 1,
                        "valueField": metric,
                        "useDataSetColors": False
                    }
                    sg = indicator["object"].mergeGraphConfig(metric,sg)
                    stockgraphs[scale].append( sg )


        stockgraphs[0].append ( {
            "title": "price",
            "useDataSetColors": False,
            "lineThickness": 2,
            "valueField": "close",
            "type": "line",
            "lineColor": "white",
            "valueAxis": "v1"
            })

        chart_corrected = 0
        amchart = []
        datasize = len(self.bot.csdata["time"])
        for i in range(0,datasize):
            if len(self.bot.csdata["time"]) > i:
                ts = time.mktime(datetime.datetime.strptime(self.bot.csdata["time"][i], "%Y-%m-%dT%H:%M:%SZ").timetuple())*1000

                if self.bot.csdata["open"][i] > 0:
                    datafields = {
                        "date": ts,
                        "open": self.bot.csdata["open"][i],
                        "close": self.bot.csdata["closed"][i],
                        "high": self.bot.csdata["high"][i],
                        "low": self.bot.csdata["low"][i],
                        "volume": self.bot.csdata["basevolume"][i]
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


        om = self.bot.getOrderManager()
        events = []
        for trade in om.getBotOrders():
            v = trade.getView(self.bot.csdata["closed"][-1])
            if v["candle_time"] is not None:
                ts = time.mktime(datetime.datetime.strptime(v["candle_time"], "%Y-%m-%dT%H:%M:%SZ").timetuple())
                if trade.order_type == Order.SELL:
                    actionText = "S"
                    actionType = "arrowDown"
                    action = "Sell"
                else:
                    actionText = "B"
                    actionType = "arrowUp"
                    action = "Buy"

                events.append({
                    "date": ts*1000,
                    "showBullet": True,
                    "showOnAxis": False,
                    "value": v["rate"],
                    "type": actionType,
                    "backgroundColor": "#85CDE6",
                    "graph": "g1",
                    "text": actionText,
                    "description": "{} Qty: {} @ {}".format(action,v["qty"],v["rate"])
                    })


        datasets = [{
            "title": self.bot.getMarket(),
            "fieldMappings": fieldmappings,
            "categoryField": "date",
            "color": "#7f8da9",
            "dataProvider": amchart,
            "stockEvents": events
        }]

        return [{ "errors": chart_corrected,"datasets":datasets,"stockgraphs":stockgraphs}]



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
        if query == "trades":
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



