import logging,time
from order import Order
from tools import Tools
from threading import Thread

class OrderManager(object):

    def __init__(self, exchange):
        self.isRunning = True
        self.exchange = exchange
        self.bot = None
        self.bot_orders = None
        self.log = logging.getLogger('crypto')
        self.openorders = []
        self.tradetick = 60
        self.trade_history= {
                "sell" : [],
                "buy" : []
                }


    def setBot(self,bot):
        self.bot = bot

    def shutdown(self):
        self.isRunning = False


    def startOrderMonitor(self,delay):
        self.log.info("setting order monitor refresh to {} seconds".format(delay))
        self.orderMonitorThread= Thread(target = self.orderMonitorLoop, args = ( delay,))
        self.orderMonitorThread.start()


    def orderMonitorLoop(self,delay = 60 ):
        while self.isRunning:
            try:
                self.log.info("update exchange balance")
                self.exchange.getBalances()
                self.getOpenOrders()
                self.log.info("refresh open orders list")
                self.syncOpenOrders()
                self.getBotOrders(refresh=True)
                self.log.info("synced orders")
            except Exception as ex:
                self.log.info("problem in ordermonitor sync loop: {}".format(ex))

            time.sleep(delay)


        self.log.info("exiting orderMonitor")


    def validate(self, order ):
        self.log.info("validating...")
        validationCheck = False

        # limit number of buy/sell trades per candle based on config
        cnt = 0
        for trade in self.getBotOrders():
            if trade.order_type == order.order_type and order.meta["candle_trade_time"] == trade.meta["candle_trade_time"]:
                cnt+=1

        if order.order_type == Order.BUY:
            m = self.bot.config.get("maxbuypercandle",0)
        else:
            m = self.bot.config.get("maxsellpercandle",0)

        if m > 0 and cnt >= m:
            self.log.info("validation failed, trade limit per candlestick {} >= {}".format(cnt,m))
            validationCheck = False
        else:
            validationCheck = True


        return validationCheck


    def tradeTick(self,tradetype):
        if self.bot.backtest:
            return False

        tick = time.time()-self.tradetick
        for trade in self.trade_history[tradetype]:
            if trade["time"] > tick:
                self.log.info("trade blocked only 1 {} trade per {} second tick".format(tradetype,self.tradetick))
                return True


    def genSellOrders(self, sellorder = None):
        """find active trade to sell"""

        if not sellorder and self.tradeTick("sell"):
            return None

        upforsale = []

        if sellorder:
            if sellorder.order_type == Order.BUY and sellorder.status == Order.FILLED:
                upforsale.append(sellorder)
        else:
            activeOrders = Order.findByBot(self.bot.getName(),self.bot.getMarket(),self.exchange.getName())
            for order in activeOrders.data["results"]:
                if order.status == Order.FILLED:
                    growth = Tools.calculateGrowth( self.bot.marketRate(), order.rate )
                    if growth and growth > self.bot.growth_target:
                        upforsale.append(order)
                    else:
                        self.log.info("order rejected, doesn't meet growth target {} < {}".format(growth,self.bot.growth_target))


        self.log.info("found {} orders up for sale".format(len(upforsale)))
        orders = []
        for orderforsale in upforsale:
            #orderforsale.status = Order.UPFORSALE
            #ref = orderforsale.save()
            #print("saving orderforsale: {} {}".format(orderforsale.ref_id,ref))
            neworder = {
                    "market": self.bot.market,
                    "created_by" : self.bot.getName(),
                    "candle_time": self.bot.analyzer.last("time"),
                    "assoc_id" : orderforsale.pkey,
                    "order_type" : Order.SELL,
                    "qty": orderforsale.qty,
                    "rate": self.bot.marketRate(),
                    "upforsale": orderforsale
                    }

            self.trade_history["sell"].append({"time":time.time(),"order": neworder})
            orders += [ neworder ]

        return orders


    def genBuyOrder(self):
        """build order structure based on bot settings"""

        if self.tradeTick("buy"):
            return None

        #get total amount in active trades
        activeOrders = Order.findByBot(self.bot.getName(),self.bot.getMarket(),self.exchange.getName())
        activeTradesSum = float(Order.sumOrders( activeOrders.data["results"] ))
        remaining_funds = self.bot.budget - activeTradesSum

        #get latest balance from the exchange
        balance = self.exchange.getBalance( self.bot.market.split("-")[0] )

        if remaining_funds > Order.DUST and balance >= remaining_funds:
            # get rate based on last market order amount
            rate = self.bot.marketRate()

            #trade amount is based on number of trades supported by the bot
            trade_amount = self.bot.budget / self.bot.tradelimit

            #determine quantity based on trade_amount
            qty = trade_amount / rate
            self.log.info("order generated")
            neworder = {
                    "created_by" : self.bot.getName(),
                    "candle_time": self.bot.analyzer.last("time"),
                    "order_type" : Order.BUY,
                    "market": self.bot.market,
                    "qty": qty,
                    "rate": rate
                    }

            self.trade_history["buy"].append({"time":time.time(),"order": neworder})
            return neworder
        else:
            self.log.info("trade rejected, out of budget")


    def getBotOrders(self,refresh=False):
        if refresh or self.bot_orders is None:
            results = Order.findByBot(self.bot.getName(),self.bot.getMarket(),self.exchange.getName())
            self.bot_orders = results.data["results"]
            self.recalculateBudget()


        return self.bot_orders


    def recalculateBudget(self):
        totalProfit = 0
        for order in self.bot_orders:
            if order.order_type == order.BUY and order.status == Order.COMPLETED:
                profit = order.getView()["profit"]
                totalProfit += profit

        self.bot.budget = self.bot.initial_budget + totalProfit
        self.bot.config["budget"] = self.bot.initial_budget + totalProfit



    def processSignal(self):
        order = None
        botsignal = self.bot.getSignal()

        if botsignal.get("signal") == "buy":
            order = self.genBuyOrder()
            if order:
                self.log.info("generated buy order: {}".format(order))
                self.send(Order(order))

        elif botsignal.get("signal") == "sell":
            orders = self.genSellOrders()
            for order in orders:
                self.log.info("generated sell order: {}".format(order))
                self.send(Order(order))


    def getOpenOrders(self):
        openorders = Order.findByBotActive(self.bot.getName(), self.bot.getMarket(),self.exchange.getName())
        self.openorders = openorders.data["results"]

    def checkStops(self):
        stopped= 0
        rate = self.bot.marketRate()
        for order in self.openorders:
            if order.status == Order.FILLED:
                g = Tools.calculateGrowth( rate, order.rate)
                if g < self.bot.stop_loss:
                    self.log.info("{} stop loss triggered on {} with {} drop".format(order.market,order.ref_id,g))
                    sellorders = self.genSellOrders(order)
                    for sellorder in sellorders:
                        if sellorder:
                            self.send( Order(sellorder),force=True )
                            stopped += 1


        #if stopped > 0:
        #    self.syncOpenOrders()

        return stopped


    def syncOpenOrders(self):
        total = 0
        for order in self.openorders: #openorders.data["results"]:
            if self.exchange.syncOrder(order):
                total += 1

        return total


    def send(self, order, force = False ):
        self.log.info("inside send")
        if force or self.validate(order):
            if force:
                order.meta["forced"] = True

            if order.upforsale:
                self.log.info("setting order {} upforsale".format(order.upforsale.ref_id))
                order.upforsale.status = Order.UPFORSALE
                order.upforsale.save()

            res = self.exchange.processOrder( order )
            self.getBotOrders(refresh=True)
            return res
