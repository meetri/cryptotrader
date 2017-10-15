import os,sys,talib,numpy,math
from influxdbwrapper import InfluxDbWrapper
from macd import MACD
from bollingerbands import BBands
from coincalc import CoinCalc
from exchange import Exchange

class Trader(object):

    def __init__(self, market = None, currency = None):
        self.influxdb = InfluxDbWrapper.getInstance()
        self.market = market
        self.cs = None
        self.indicators = None
        if currency is not None:
            self.market = CoinCalc.getInstance().get_market(currency)


    def set_currency(self,currency):
        self.market = CoinCalc.getInstance().get_market(currency)
        return self


    def get_indicator_size(self):
        return len(self.cs["time"])

    def set_default(self,val,idx,default = float(0)):

        try:
            v = val[idx]
        except:
            v = default

        if v and not numpy.isnan(v):
            return v
        else:
            return default

    def get_indicator_index(self,idx):
        if self.indicators is None:
            self.get_indicators()

        if idx < len( self.cs["time"]):
            rsi_v = self.set_default(self.indicators["rsi"],idx)
            mfi_v = self.set_default(self.indicators["mfi"],idx)
            cci_v = self.set_default(self.indicators["cci"],idx)
            cmo_v = self.set_default(self.indicators["cmo"],idx)
            mom_v = self.set_default(self.indicators["mom"],idx)
            dx_v = self.set_default(self.indicators["dx"],idx)
            roc_v = self.set_default(self.indicators["roc"],idx)

            macd_v = self.set_default(self.indicators["macd"][0],idx)
            macdsig_v = self.set_default(self.indicators["macd"][1],idx)
            macdhist_v = self.set_default(self.indicators["macd"][2],idx)

            bb_u = self.set_default(self.indicators["bb"][0],idx)
            bb_m = self.set_default(self.indicators["bb"][1],idx)
            bb_l = self.set_default(self.indicators["bb"][2],idx)

            bb2_u = self.set_default(self.indicators["bb2"][0],idx)
            bb2_m = self.set_default(self.indicators["bb2"][1],idx)
            bb2_l = self.set_default(self.indicators["bb2"][2],idx)

            return {
                    "time": self.cs["time"][idx],
                    "rsi":rsi_v,
                    "mfi":mfi_v,
                    "cci":cci_v,
                    "cmo":cmo_v,
                    "mom":mom_v,
                    "dx":dx_v,
                    "roc":roc_v,
                    "macd":macd_v,
                    "macdsig":macdsig_v,
                    "macdhist":macdhist_v,
                    "bb_u":bb_u,
                    "bb_m":bb_m,
                    "bb_l":bb_l,
                    "bb2_u":bb2_u,
                    "bb2_m":bb2_m,
                    "bb2_l":bb2_l
                    }


    def get_indicators(self):
        rsi  = self.get_rsi()
        mfi  = self.get_mfi()
        cci  = self.get_cci()
        cmo  = self.get_cmo()
        mom  = self.get_mom()
        dx  = self.get_dx()
        macd = MACD(self.cs).get_macd()
        bb = BBands(self.cs,timeperiod=5).get_bb()
        bb2 = BBands(self.cs,timeperiod=5,nbdevup=1,nbdevdn=1).get_bb()
        roc  = self.get_roc()
        self.indicators = {
                "rsi":rsi,
                "mfi":mfi,
                "cci":cci,
                "cmo":cmo,
                "mom":mom,
                "dx":dx,
                "macd":macd,
                "bb": bb,
                "bb2": bb2,
                "roc":roc
                }
        return self.indicators


    def get_mom(self,period=10):
        try:
            res = talib.MOM( self.cs["closed"], period )
        except:
            res = None
        return res

    def get_dx(self,period=14):
        try:
            res = talib.DX(  self.cs["high"] , self.cs["low"], self.cs["closed"], period )
        except:
            res = None
        return res

    def get_rsi(self,period=14):
        try:
            res = talib.RSI (self.cs["closed"], period )
        except Exception as ex:
            #print(self.cs["closed"])
            #print("talib exception: {}".format(ex))
            res = None

        return res

    def get_cmo(self,period=20):
        try:
            res = talib.CMO (self.cs["closed"], period )
        except:
            res = None
        return res

    def get_roc(self,period=10):
        try:
            res = talib.ROC (self.cs["closed"], period )
        except:
            res = None
        return res




    def get_cci(self,period=20):
        try:
            res = talib.CCI(  self.cs["high"] , self.cs["low"], self.cs["closed"], period )
        except:
            res = None
        return res

    def get_mfi(self,period=14):
        try:
            mfi = talib.MFI( self.cs["high"], self.cs["low"],self.cs["closed"], self.cs["volume"], period )
        except:
            mfi = None
        return mfi

    def get_candlesticks(self, timeframe = "1h", size = "5m" ):
        points = self.influxdb.raw_query("""select FIRST(last) as open, LAST(last) as closed, MAX(last) as high, MIN(last) as low, (LAST(basevolume)+LAST(volume)) as volume FROM "market_summary" WHERE marketname='{}' and time > now() - {} group by time({})""".format(self.market,timeframe,size)).get_points()

        cs = self.clear_candlesticks()
        for point in points:
            cs["low"].extend([point["low"]])
            cs["high"].extend([point["high"]])
            cs["closed"].extend([point["closed"]])
            cs["open"].extend([point["open"]])
            cs["volume"].extend([point["volume"]])
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
        fix_gaps(cs["time"])

        self.cs = {
                "low": numpy.array(cs["low"]),
                "high": numpy.array(cs["high"]),
                "closed": numpy.array(cs["closed"]),
                "volume": numpy.array(cs["volume"]),
                "open": numpy.array(cs["open"]),
                "time": cs["time"]
                }

        Exchange.getInstance().set_market_value(self.market, self.cs["closed"][-1] )
        return self.cs


    def clear_candlesticks(self):
        return { "open": [], "closed": [], "high": [], "low": [], "volume": [],"time":[], "opening":[],"closing":[] }









