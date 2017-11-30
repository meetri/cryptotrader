import logging,uuid
from exchangemanager import ExchangeManager
from result import Result
from order import Order

class BacktestManager(ExchangeManager):

    def __init__(self, config = {} ):
        ExchangeManager.__init__(self, "BTEST", config )
        self.balance = None
        self.log = logging.getLogger('crypto')


    def processOrder(self, order ):
        order.setExchange( self.getName() )
        self.log.info("backtest exchange processing order")
        if order.rate != order.MARKET:
            r = { "uuid" : "test-{}".format(uuid.uuid4()) }

            order.ref_id = r["uuid"]
            order.status = order.OPEN

            order.meta["api"] = {
                    "create": r
                    }

            res = order.save()
            self.log.info("save results {}".format(res))
            return Result(True,"success",r)
        else:
            return Result.fail("Market orders not allowed on bittrex")


    def syncOrder(self,order):
        if order.status < order.TERMINATED_STATE:
            status = order.status
            #results = self.api.account_get_order( order.ref_id )
            #data = results.getData()

            if order.order_type == Order.SELL:
                order.status = Order.COMPLETED
            elif order.order_type == Order.BUY:
                order.status = Order.FILLED

            if status != order.status:
                order.save()
                if order.status == order.COMPLETED:
                    assocorder = Order.findById(order.assoc_id)
                    if assocorder.isOk():
                        aorder = assocorder.data["results"][0]
                        aorder.status = Order.COMPLETED
                        self.log.info("found associated order {}".format(aorder.ref_id))
                        aorder.meta["sold_at"] = float(order.rate)
                        aorder.assoc_id = order.pkey
                        res = aorder.save()
                        self.log.info("saved associated order {}".format(res))


                return True


    def getBalance(self,currency):
        return 10000

    def getBalances(self):
        return {}
