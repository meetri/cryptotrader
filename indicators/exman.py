import sys,io,logging,time
from bittrex import Bittrex

class ExchangeManager(object):

    _instance = None

    def __init__(self):
        self.log = logging.getLogger('crypto')
        self.api = Bittrex()
        self.active_trades = []
        self.completed_trades = []
        self.history = {}


    def checkin(self,bot):
        botname = bot.get_name()
        if botname in self.history:
            self.history[botname]["entered"] += 1
        else:
            self.history[botname] = {
                    "entered": 1,
                    "rejected": 0,
                    "sells": 0,
                    "buys": 0,
                    "trades": 0,
                    "last_entered": None,
                    "last_sell": None,
                    "last_buy": None,
                    "last_trade": None,
                    }

        return self.history[botname]


    def checkout(self, bot):
        self.history[bot.get_name()]["last_entered"] = time.time()

    def get_history(self,bot):
        return self.history[bot.get_name()]


    def validate_trade(self,bot,trade):
        # make sure the last trade wasn't the same amount
        # make sure ...
        if trade.demo:
            self.log.info("trade rejected because it's in demo mode")
            return False


        return True

    def update_exchange_status(self,trade, forcethrough = True ):
        if "uuid" in trade.meta:

            #if forcethrough or "details" not in trade.meta or trade.meta["details"]["IsOpen"] == True or trade.meta["details"]["IsOpen"] == "true":
            if "uuid" in trade.meta:
                try:
                    self.log.info("get trade details trade: {}".format(trade.meta["uuid"]))
                    res = Bittrex().account_get_order(trade.meta["uuid"]).getData()
                    if res["success"]:
                        trade.meta["details"] = res["result"]
                        if trade.meta["details"]["IsOpen"] == False or trade.meta["details"]["IsOpen"] == "false":
                            #TODO: Handle cancelled state...
                            if trade.meta["details"]["CancelInitiated"] == True:
                                trade.status = "cancelled"
                            elif trade.meta["details"]["Type"] == "LIMIT_SELL":
                                trade.status = "sold"
                            else:
                                trade.status = "holding"

                        trade.save()

                except Exception as ex:
                    self.log.error("update_exchange_status failed withh {}".format(ex))
                    trade.meta["last_error"] = "update_exchange_status failed with {}".format(ex)
                    trade.save()
            else:
                self.log.info("trade is already marked as closed")
        else:
            self.log.info("uuid not found in meta data")


    def cancel_trade(self,trade):
        if "uuid" in trade.meta:

            if "details" not in trade.meta or trade.meta["details"]["IsOpen"] == True or trade.meta["details"]["IsOpen"] == "true":
                try:
                    self.log.info("cancelling trade: {}".format(trade.meta["uuid"]))
                    res = Bittrex().market_cancel(trade.meta["uuid"]).getData()
                    if res["success"]:
                        trade.meta["cancelled_response"] = res
                    else:
                        if res["message"] == "ORDER_NOT_OPEN":
                            trade.status = "cancelled"
                            trade.save()
                        else:
                            self.log.error("unexpected error while cancelling trade: {}".format(res["message"]))
                            return False

                    trade.status = "cancelled"
                    trade.save()

                    self.update_exchange_status(trade,forcethrough=True)

                except Exception as ex:
                    self.log.error("cancel_trade failed with {}".format(ex))
                    trade.meta["last_error"] = "cancel_trade failed with {}".format(ex)
                    trade.save()
            else:
                self.log.info("trade has aleady been cancelled")
        else:
            self.log.info("uuid not found in meta data")


    def send_trade(self,trade):
        try:

            res = None
            if trade.trade_type == "buy":
                res = Bittrex().market_buylimit(trade.market,trade.quantity,trade.price).getData()
            elif trade.trade_type == "sell":
                res = Bittrex().market_selllimit(trade.market,trade.quantity,trade.price).getData()
            else:
                self.log.info("error in trade_type {}".format(trade.trade_type))

            if res:
                if res["success"]:
                    trade.status = "open"
                    trade.meta["uuid"] = res["result"]["uuid"]
                    trade.save()
                    self.update_exchange_status( trade )

        except Exception as ex:
            self.log.error("perform_trade failed with {}".format(ex))



    def bot_trade(self, bot ):
        self.checkin(bot)

        trade = bot.gen_trade()
        if trade and self.validate_trade(bot,trade):
            trade.save()
            if trade.order_type in ["instant","market","limit"]:
                self.send_trade(trade)
            elif trade.order_type == "trailing":
                #TODO follow the trend's burst to it's end prior to executing the trade
                bestseller = BestSeller(bot,trade,"1m")
                trade.botmanager = bestseller
                #self.send_trade(trade)
                pass
            else:
                self.log.warn("unknown order_type: {}".format(trade.order_type))
            bot.monitor_trade(trade)
        else:
            self.log.info("trade rejected")
            bot.reject_trade(trade)

        self.checkout(bot)
        pass



