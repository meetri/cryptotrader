import os,sys,time
from basebot import BaseBot
from threading import Thread

class TradeManager(BaseBot):

    def __init__(self,market):
        BaseBot.__init__(self,market,"TradeManager")
        self.botlist = []
        self.done = False


    def monitor_trades(self,bot):
        self.botlist += [bot]


    def update_trade_status(self, bot ):
        for trade in bot.trades:
            if trade.status in ["open","sold"] and trade.trade_type == "sell":
                if trade.status == "open":
                    trade.update_exchange_status()
                if trade.status == "sold":
                    if trade.meta.get("related_trade_id"):
                        buy_trade = bot.find_trade_by_id( trade.meta.get("related_trade_id") )
                        if buy_trade:
                            buy_trade.meta["sell_trade_details"] = trade.details()
                            buy_trade.status = "done"
                            buy_trade.save()
                            trade.status = "done"
                            trade.save()
                        else:
                            self.log.info("can't find associated buy trade in bot trade list")
                    else:
                        self.log.info("can't find trade meta data for related trade id")
            elif trade.status == "open" and trade.trade_type == "buy":
                trade.update_exchange_status()

                #TODO: determine if trade is expired and cancel


    def monitor_thread(self,pollfrequency=15):

        while not self.done:
            for bot in self.botlist:
                self.update_trade_status(bot)
            time.sleep(pollfrequency)



    def start(self,pollfrequency = 15 ):
        self.log.info("staring {}".format(self.get_name()))
        thread = Thread(target = self.monitor_thread, args = ( pollfrequency,))
        thread.start()

    def process(self):
        BaseBot.process(self)

        #this should be ran in it's own thread

