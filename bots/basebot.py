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
        self.trade_quantity = 0.0001
        self.trades = []
        self.rejected_trades = []
        self.load_active_trades()
        self.last_trade_time = None
        self.minimum_trade_frequency = 60


    def load_active_trades(self):
        self.trades = Trade.load_by_manager(self.name)
        self.log.info("loading active trades, found: {}".format(len(self.trades)))


    def get_monitored_trades(self):
        return self.trades


    def get_rejected_trades(self):
        return self.rejected_trades


    def monitor_trade(self, trade ):
        self.last_trade_time = time.time()
        self.trades += [trade]


    def reject_trade(self,trade):
        self.rejected_trades += [trade]


    def get_details(self):
        return {
                "name": self.get_name()
                }


    def gen_trade(self, order_type = "limit"):

        if self.last_trade_time and self.last_trade_time + self.minimum_trade_frequency > time.time():
            # block this trade...
            return

        last = Exchange.getInstance().get_market_value( self.market )
        if self.trade_price is None:
            self.trade_price = last

        trade_type = None
        sell_trade = None

        if self.signal == "overbought":
            for trade in self.trades:
                if trade.forsale(last,minbuy=True):
                    trade_type = "sell"
                    sell_trade = trade
                    self.quantity = sell_trade.quantity
                    break

            if sell_trade == None:
                self.log.info("no buy trades to sell")

        elif self.signal == "oversold":
            if Wallet.getInstance().buy_budget(self.market,self.trade_price):
                trade_type = "buy"
            else:
                self.log.info("you are out of budget to buy")

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

