import os,sys,talib,numpy,math
from influxdbwrapper import InfluxDbWrapper
from coincalc import CoinCalc
from exchange import Exchange

class Trader(object):

    def __init__(self, market = None, currency = None):
        self.influxdb = InfluxDbWrapper.getInstance()
        self.market = market
        self.cs = None
        self.indicators = None
        self.timeframe = None
        self.cssize = None
        if currency is not None:
            self.market = CoinCalc.getInstance().get_market(currency)


    def set_currency(self,currency):
        self.market = CoinCalc.getInstance().get_market(currency)
        return self


    def get_candlesticks(self, timeframe = "1h", size = "5m", dateOffset = "now()" ):
        self.timeframe = timeframe
        self.cssize = size
        points = self.influxdb.raw_query("""select LAST(basevolume) as basevolume, LAST(volume) as volume, FIRST(last) as open, LAST(last) as closed, MAX(last) as high, MIN(last) as low FROM "market_summary" WHERE marketname='{0}' and time < {1} and time > {1} - {2}  group by time({3})""".format(self.market,dateOffset,timeframe,size)).get_points()

        cs = self.clear_candlesticks()

        psize = 0
        for point in points:
            psize += 1
            cs["low"].extend([point["low"]])
            cs["high"].extend([point["high"]])
            cs["closed"].extend([point["closed"]])
            cs["open"].extend([point["open"]])
            cs["volume"].extend([point["volume"]])
            cs["basevolume"].extend([point["basevolume"]])
            cs["time"].extend([point["time"]])

        if psize == 0:
            raise Exception("no market data for {} at {}".format(self.market,dateOffset))

        def fix_gaps(lst):
            for idx,val in enumerate(lst):
                if val == None:
                    if idx > 0:
                        lst[idx] = lst[idx-1]
                    if idx == 0:
                        lst[idx] = 0

        fix_gaps(cs["low"])
        fix_gaps(cs["high"])
        fix_gaps(cs["closed"])
        fix_gaps(cs["open"])
        fix_gaps(cs["volume"])
        fix_gaps(cs["basevolume"])
        fix_gaps(cs["time"])


        self.cs = {
                "low": numpy.array(cs["low"]),
                "high": numpy.array(cs["high"]),
                "closed": numpy.array(cs["closed"]),
                "volume": numpy.array(cs["volume"]),
                "basevolume": numpy.array(cs["basevolume"]),
                "open": numpy.array(cs["open"]),
                "time": cs["time"]
                }

        Exchange.getInstance().set_market_value(self.market, self.cs["closed"][-1] )
        return self.cs

    def xget_candlesticks(self, timeframe = "1h", size = "5m" ):
        self.timeframe = timeframe
        self.cssize = size
        points = self.influxdb.raw_query("""select FIRST(last) as open, LAST(last) as closed, MAX(last) as high, MIN(last) as low, (LAST(basevolume)+LAST(volume)) as volume FROM "market_summary" WHERE marketname='{}' and time > now() - {} group by time({})""".format(self.market,timeframe,size)).get_points()

        cs = self.clear_candlesticks()

        for point in points:
            cs["low"].extend([point["low"]])
            cs["high"].extend([point["high"]])
            cs["closed"].extend([point["closed"]])
            cs["open"].extend([point["open"]])
            cs["volume"].extend([point["volume"]])
            cs["basevolume"].extend([point["basevolume"]])
            cs["time"].extend([point["time"]])

        def fix_gaps(lst):
            for idx,val in enumerate(lst):
                if val == None:
                    if idx > 0:
                        lst[idx] = lst[idx-1]
                    if idx == 0:
                        lst[idx] = 0

        fix_gaps(cs["low"])
        fix_gaps(cs["high"])
        fix_gaps(cs["closed"])
        fix_gaps(cs["open"])
        fix_gaps(cs["volume"])
        fix_gaps(cs["basevolume"])
        fix_gaps(cs["time"])


        self.cs = {
                "low": numpy.array(cs["low"]),
                "high": numpy.array(cs["high"]),
                "closed": numpy.array(cs["closed"]),
                "volume": numpy.array(cs["volume"]),
                "basevolume": numpy.array(cs["basevolume"]),
                "open": numpy.array(cs["open"]),
                "time": cs["time"]
                }

        Exchange.getInstance().set_market_value(self.market, self.cs["closed"][-1] )
        return self.cs


    def clear_candlesticks(self):
        return { "open": [], "closed": [], "high": [], "low": [], "volume": [], "basevolume": [], "time":[], "opening":[],"closing":[] }


