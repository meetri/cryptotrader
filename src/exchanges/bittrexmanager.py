import logging
from exchangemanager import ExchangeManager
from bittrex import Bittrex
from result import Result
from order import Order

class BittrexManager(ExchangeManager):

    def __init__(self, config = {} ):
        ExchangeManager.__init__(self, "BTRX", config )
        self.api = Bittrex()
        self.balance = None
        self.log = logging.getLogger('crypto')


    def processOrder(self, order ):
        order.setExchange( self.getName() )
        self.log.info("bittrex exchange processing order")
        if order.rate != order.MARKET:
            if order.order_type == order.SELL:
                r = self.api.market_selllimit( order.market, order.qty, order.rate ).getData()
            elif order.order_type == order.BUY:
                r = self.api.market_buylimit( order.market, order.qty, order.rate ).getData()

            if r["success"]:
                order.ref_id = r["result"]["uuid"]
                order.status = order.OPEN
            else:
                order.status = order.ERROR

            order.meta["api"] = {
                    "create": r
                    }
            res = order.save()
            self.log.info("save results {}".format(res))
            return Result(r["success"],r["message"],r["result"])
        else:
            return Result.fail("Market orders not allowed on bittrex")


    def syncOrder(self,order):
        if order.status < order.TERMINATED_STATE:
            status = order.status
            results = self.api.account_get_order( order.ref_id )
            data = results.getData()
            if data["success"]:
                res = data["result"]
                if res["CancelInitiated"]:
                    order.status = order.CANCELLED
                elif not res["IsOpen"] and res["Type"] == "LIMIT_SELL":
                    order.status = order.COMPLETED
                elif not res["IsOpen"] and res["Type"] == "LIMIT_BUY":
                    order.status = order.FILLED
                elif res["IsOpen"] and not res["Quantity"] > res["QuantityRemaining"] and order.status != order.PARTIAL_FILL:
                    order.status = order.PARTIAL_FILL

                if status != order.status or "state" not in order.meta["api"]:
                    self.log.info("found updates to order {}".format(order.ref_id))
                    order.meta["api"]["state"] = data
                    order.save()
                    if order.status == order.COMPLETED: # and order.order_type == Order.SELL:
                        self.log.info("looking for associated order: {}".format(order.assoc_id))
                        assocorder = Order.findById(order.assoc_id)
                        if assocorder.isOk():
                            aorder = assocorder.data["results"][0]
                            aorder.status = Order.COMPLETED
                            self.log.info("found associated order {}".format(aorder.ref_id))
                            #instead get this rate from the api results...
                            aorder.meta["sold_at"] = data["result"]['PricePerUnit']
                            aorder.assoc_id = order.pkey #data["result"]['PricePerUnit']
                            res = aorder.save()
                            self.log.info("saved associated order {}".format(res))

                    return True


    def getBalance(self,currency):
        if self.balance is None:
            self.getBalances()

        currency = currency.upper()
        if currency in self.balance:
            return self.balance[currency]["Available"]


    def getBalances(self):
        results = self.api.account_get_balances().getData()
        if results["success"]:
            self.balance = {}
            for c in results["result"]:
                self.balance[c["Currency"]] = c

        return self.balance


