import os,sys,logging,time,json,datetime,random
from trader import Trader
from marketanalyzer import Analyzer
from botdata import BotDataProvider

class BaseBot(object):

    OVERBOUGHT = 100
    OVERSOLD = 200

    #def __init__(self, market,budget, tradelimit, candlestick = "5m",timeframe = "24h",  name = None, config = {} ):
    def __init__(self, name, config):

        self.cycles = 0
        self.config = config
        self.name = name
        self.market = config.get("market",None)
        self.budget = config.get("budget",0)
        self.initial_budget = self.budget
        self.tradelimit = config.get("tradelimit",0)

        if not self.market:
            raise Exception("missing required fields market: {}, budget: {}, tradelimit: {}".format(self.market,self.budget,self.tradelimit))

        self.candlestick=config.get("candlestick","5m")
        self.timeframe=config.get("timeframe","24h")
        self.growth_target = config.get("growthtarget",2)
        self.stop_loss = config.get("stoploss",3)
        self.signal = None
        self.results = {}

        #dataprovider for candlestick data
        self.trader = Trader(market=self.market)

        #candlestick data
        self.csdata = None

        #manage indicators
        self.analyzer = None

        #manage orders
        self.ordermanager = None

        #keep track of latest indicator and bot signals
        self.signal_history = {}
        self.all_signals = []

        self.log = logging.getLogger('crypto')

        # debug messages passed to bot client
        self.debug = []

        #aggregate bot data for bot client
        self.data_provider = BotDataProvider(self)

        #enable backtesting...
        self.backtest = config.get("backtest",False)
        ofs  = config.get("backtest_start_ofs",259200)
        ts = time.time() - ofs
        ts = ts - ( ts % 3600 ) - config.get("run_offset",0)
        self.backtest_tick = ts
        self.backtest_startprice = None
        self.backtest_endprice = 0

        self.run_interval = config.get("run_interval",300)

        if self.backtest:
            random.seed()
            rid = random.randint(100,70000)
            self.name = "{}-{}".format(name,rid)


    def stopBackTest(self):
        self.backtest = False
        self.log.info("backtest completed")


    def marketRate(self,index=1):
        return self.analyzer.last("closed",index)


    def getOrderManager(self):
        return self.ordermanager


    def setOrderManager(self,om):
        self.ordermanager = om
        self.ordermanager.setBot(self)
        self.log.info("initializing order manager")
        self.ordermanager.startOrderMonitor(5)


    def getSignal(self):
        return self.signal


    def checkSignal(self,name,signal,timepassed):
        checktime = time.time() - timepassed
        if name in self.signal_history and self.signal_history[name]["time"] > checktime:
            self.debug.append("checksignal {} triggered".format(name))
            return self.signal_history[name]["strength"]

        return None


    def pushSignal(self,name,signal,strength,minor=False):

        if strength is not None:
            sig = {
                    "name": self.getName(),
                    "signal" : signal,
                    "rate": self.marketRate(),
                    "cstime": self.analyzer.last("time"),
                    "time": time.time(),
                    "strength": strength,
                    "count": 1
                    }

            if not minor:
                if self.signal and self.signal["name"] == sig["name"] and self.signal["cstime"] == sig["cstime"]:
                    self.signal["count"] += 1
                else:
                    self.signal = sig

            if name in self.signal_history and self.signal_history[name]["cstime"] == sig["cstime"]:
                self.signal_history[name]["count"] +=  1
            else:
                self.signal_history[name] = sig
                if not minor:
                    self.all_signals.append(sig)

    def debug_reset(self):
        self.debug = []

    def append_debug_message(self,msg):
        self.debug.append(msg)

    def get_debug_messages(self):
        return self.debug

    def process(self):
        res = None

        if self.getSignal():
            res =  self.getOrderManager().processSignal()

        self.getOrderManager().checkStops()

        self.cycles += 1
        return res


    def refreshCandlesticks(self):
        if self.backtest:
            bt_time = "{}s".format(int(self.backtest_tick))
            self.csdata = self.trader.get_candlesticks(self.timeframe,self.candlestick,dateOffset=bt_time)
            self.backtest_endprice = self.csdata["closed"][-1]
            if self.backtest_startprice is None:
                self.backtest_startprice = self.csdata["closed"][-1]
            self.backtest_tick += self.run_interval
            if self.backtest_tick > time.time():
                self.log.info("backtest complete")
                self.backtest_tick = time.time()
        else:
            self.csdata = self.trader.get_candlesticks(self.timeframe,self.candlestick)

        self.analyzer = Analyzer( self.csdata )
        self.signal = None
        return self.analyzer


    def getAnalyzer():
        return self.analyzer

    def getMarket(self):
        return self.market

    def getName(self):
        return self.name

    def getIndicators(self):
        return self.indicators

    def dataProvider(self):
        return self.data_provider

    def info(self):
        return {
                "name": self.name,
                "cycle": self.cycles,
                "signal": self.signal,
                "last": self.marketRate(),
                "time" : self.analyzer.last("time"),
                "servertime": time.strftime("%c"),
                "config": self.config
                }



