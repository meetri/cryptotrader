import os,sys,logging,time
from trader import Trader
from wallet import Wallet
from exchange import Exchange
from trade import Trade

class BaseBot(object):

    def __init__(self, market, name = None ):
        self.log = logging.getLogger('crypto')
        self.indicators = []
        self.market = market
        self.trader = Trader(market=market)
        self.csdata = None
        self.name = name
        self.results = {}
        self.signal = None
        self.trade_price = None
        self.trades = []
        self.rejected_trades = []
        self.load_active_trades()
        self.last_trade_time = None
        self.last_trade_price = None
        self.trade_quantity = 0.01
        self.minimum_trade_frequency = 120
        self.max_ongoing_trades = 10
        self.trade_price_gap = 0
        self.debug = []
        self.signal_monitor = {}

        # lag signal by about 30 seconds...
        self.signal_lagtime = 30


    def get_monitor_signal(self, label ):
        return self.signal_monitor.get(label)["signal"]


    def signal_last_triggered( self, name ):
        if name in self.signal_monitor:
            return self.signal_monitor[name]["last_triggered"]


    def trigger_signal(self, name ):
        if name in self.signal_monitor:
            self.signal_monitor[name]["last_triggered"] = time.time()


    def track_signals(self, signals ):
        """keep track for how long a particular signal has been on"""

        for signal in signals:
            analysis = signals[signal].get("analysis",{})
            if signal not in self.signal_monitor or analysis.get("signal") != self.signal_monitor[signal].get("signal"):
                self.signal_monitor[signal] = {
                    "signal": signals[signal].get("signal"),
                    "last_triggered": None,
                    "timestamp": time.time()
                }


    def get_debug_messages(self):
        return self.debug

    def load_active_trades(self):
        self.trades = Trade.load_by_manager(self.name)
        self.log.info("loading active trades, found: {}".format(len(self.trades)))

    def find_trade_by_id(self,idx):
        for trade in self.trades:
            if trade.pkey == idx:
                return trade


    def get_monitored_trades(self):
        return self.trades


    def get_rejected_trades(self):
        return self.rejected_trades


    def monitor_trade(self, trade ):
        self.last_trade_time = time.time()
        self.last_trade_price = trade.price
        self.trades += [trade]


    def reject_trade(self,trade):
        self.rejected_trades += [trade]


    def get_details(self):
        return {
                "name": self.get_name()
                }

    def get_active_trades(self):
        count = 0
        for trade in self.trades:
            if trade.status in ["open","holding"]:
                count += 1
        return count


    def gen_trade(self, order_type = "limit"):

        last = Exchange.getInstance().get_market_value( self.market )
        if self.trade_price is None:
            self.trade_price = last

        if self.signal == "oversold":
            if self.last_trade_time and self.last_trade_time + self.minimum_trade_frequency > time.time():
                self.log.info("blocked - for {} seconds".format( (self.last_trade_time+self.minimum_trade_frequency) - time.time()))
                self.debug += ["blocked - for {} seconds".format( (self.last_trade_time+self.minimum_trade_frequency) - time.time())]
                # block this trade...
                return

            if self.get_active_trades() >= self.max_ongoing_trades:
                self.log.info("blocked - max allowed trade count reached")
                self.debug += ["blocked - max allowed trade count reached"]
                return

            if self.last_trade_price == self.trade_price:
                self.log.info("blocked - trade unit price same as previous trade")
                self.debug += ["blocked - trade unit price same as previous trade"]
                return

            #TODO . block if sell and open sell, and  sell amount is greater than open sell amount...
            #TODO . block if buy and open buy, and buy is less than open buy
            #TODO . block if buy and most recent buy is less
            #TODO . externalize guard rules... ( different protections for different types of bots )

        trade_type = None
        sell_trade = None

        if self.signal == "overbought":
            for trade in self.trades:
                if trade.forsale(last,minbuy=False):
                    trade_type = "sell"
                    if sell_trade:
                        if trade.details()["change"] > sell_trade.details()["change"]:
                            sell_trade = trade
                    else:
                        sell_trade = trade

            if sell_trade == None:
                self.log.info("no buy trades to sell")
                self.debug += ["no buy trades to sell at this time"]
                return
            else:
                sell_trade.hold = True
                self.quantity = sell_trade.quantity

        elif self.signal == "oversold":
            if Wallet.getInstance().buy_budget(self.market,self.trade_price):
                trade_type = "buy"
            else:
                self.log.info("you are out of budget to buy")
                self.debug += ["you have no money to buy anyting"]


        if self.trade_price_gap > 0:
            if trade_type == "buy":
                self.trade_price = self.trade_price + self.trade_price_gap
            elif trade_type == "sell":
                self.trade_price = self.trade_price - self.trade_price_gap

        if trade_type:
            newtrade = Trade({
                "market": self.market,
                "quantity": self.trade_quantity,
                "price": self.trade_price,
                "trade_type": trade_type,
                "order_type": order_type,
                "managed_by": self.name,
                "created_by": self.name,
                "modified_by": self.name,
                "meta": {
                    "bot_source": self.get_details(),
                    "details": {}
                    }
                })

            #reset trade price
            self.trade_price = None

            if sell_trade:
                sell_trade.sign_trade(newtrade)

            return newtrade


    def get_tradeprice(self):
        return self.trade_price


    def get_signal(self):
        return self.signal


    def get_name(self):
        return self.name


    def get_indicators(self):
        return self.indicators

    def check_overrides(self):
        buyfile = "/tmp/buy_override"
        sellfile = "/tmp/sell_override"

        if os.path.isfile(buyfile):
            self.log.info("buy override initiated")
            self.signal = "oversold"
            os.remove(buyfile)
        elif os.path.isfile(sellfile):
            self.log.info("sell override initiated")
            self.signal = "overbought"
            os.remove(sellfile)


    def set_results(self,results):
        self.check_overrides()
        self.results = results


    def get_results(self):
        return self.results


    def process(self):
        return self

