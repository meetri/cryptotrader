"""
OBSOLETE - DELETE THIS FILE !! - now called order.py
"""
import os,sys,logging,time,json
import psycopg2.extras
from exchange import Exchange
from pgwrapper import PgPool
from exman import ExchangeManager
from collections import OrderedDict

class Trade(object):

    def __init__(self, tdata = {} ):
        self.demo = False

        self.log = logging.getLogger('crypto')
        self.exchange = Exchange.getInstance()
        self.dbdata = tdata
        self.unserialize(tdata)
        self.exman = ExchangeManager()

        self.pgpool = PgPool.getInstance()

        #protections
        self.max_trade_quantity = 0.01
        self.max_trade_frequency = 120    #seconds

        self.increase_goal = 0.01

        self.hold = False


    def sign_trade(self,trade):
        trade.meta["related_trade_id"] = self.pkey
        return trade


    def forsale(self,amount, minbuy=False):
        if self.hold:
            return False

        details = self.details()
        if self.trade_type == "buy" and self.status in ["holding"]:
            if minbuy and (amount > details["breakeven"]):
                return True
            elif amount > details["goal"]:
                return True
        else:
            return False


    def validate(self):
        if self.quantity > 0 and self.quantity <= self.max_trade_quantity:
            if len(self.market) > 0 and len(self.created_by) > 0 and len(self.managed_by) > 0:
                if self.trade_type in ["buy","sell"] and  self.order_type in ["limit","market","instant","demo","trailing"]:
                    if self.status in ["closed","new","sold","cancelled","holding","open","done"]:
                        return True
                    else:
                        self.log.info("status: '{}' is not expected".format(self.status))
                else:
                    self.log.info("validation failed trade_type / order_type is invalid {} / {}".format(self.trade_type,self.order_type))
            else:
                self.log.info("missing market, created by, or managed by info".format(self.market,self.created_by,self.managed_by))
        else:
            self.log.info("trade quantity is outside the alloweable bounds {} ? {}".format(self.quantity,self.max_trade_quantity))

        return False


    def save(self):
        if self.validate():
            if not self.dbdata or not self.pkey:
                self.log.info('creating new trade record')
                return self.create()
            else:
                self.log.info('updating a trade record')
                return self.update()
        else:
            self.log.error("unable to save invalid trade")



    def create(self):
        ser = self.serialize()
        del ser["id"]
        k = self.pgpool.insert("markets.trades", ser )
        if k:
            self.pkey = k[0]
            self.dbdata = self.serialize()
            return True


    def update(self):
        res = self.pgpool.update("markets.trades","id",self.serialize(),self.dbdata)
        if res:
            self.dbdata = self.serialize()
            return True

    def cancel(self):
        return self.exman.cancel_trade(self)

    def update_exchange_status(self):
        return self.exman.update_exchange_status(self)


    def unserialize(self, tdata):
        self.pkey = tdata.get("id",None)
        self.market = tdata.get("market")
        self.exchange = tdata.get("exchange","bittrex")
        self.quantity = float(tdata.get("quantity"))
        self.price = float(tdata.get("price"))
        self.trade_type = tdata.get("trade_type")     #buy or sell
        self.order_type = tdata.get("order_type","limit")     #limit, market, instant, demo, trailing
        self.created_by = tdata.get("created_by","default")
        self.managed_by = tdata.get("managed_by","default")
        self.status = tdata.get("status","new")
        self.created_ts = tdata.get("created_ts")
        self.created_by = tdata.get("created_by","default")
        self.modified_by = tdata.get("modified_by","default")
        self.active = tdata.get("active",True)
        self.meta = tdata.get("meta",{})
        return self


    def details(self,full = True):

        details = self.meta.get("details",{})
        currency_precision = 2

        ret = OrderedDict()
        ret["id"] = self.pkey
        if self.created_ts is not None:
            ret["time"] = self.created_ts.strftime("%c")
        ret["assoc"] = self.meta.get("related_trade_id")
        ret["market"] = self.market
        ret["trade_type"] = details.get("Trade",self.trade_type)
        ret["qty"] = details.get("Quantity",self.quantity)

        #return ret

        comres = details.get("CommissionReserved",0)
        if self.trade_type == "sell":
            ret["limit"] = details.get("Limit",self.price)
            ret["unitprice"] = details.get("PricePerUnit",self.price) or self.price
            ret["price"] = details.get("Price",self.price*self.quantity)
            ret["commission"] = details.get("CommissionPaid",comres)

        elif self.trade_type == "buy":
            sell_trade = self.meta.get("sell_trade_details",{})
            ret["limit"] = details.get("Limit",self.price)
            ret["unitprice"] = details.get("PricePerUnit",self.price) or self.price
            ret["commission"] = details.get("CommissionPaid",comres)
            ret["breakeven"] = ret["unitprice"] + ret["commission"]
            ret["goal"] = round( ret["unitprice"] + ( ret["unitprice"] * self.increase_goal ) + ret["commission"] ,currency_precision)
            ret["soldat"] = sell_trade.get("unitprice")
            trade_closed = sell_trade.get("unitprice", Exchange.getInstance().get_market_value(self.market))
            trade_growth = round(((trade_closed- float(ret["unitprice"])) / trade_closed) * 100,2)
            ret["change"] = "{}%".format(trade_growth)

        if self.hold and self.status == "holding":
            ret["status"] = "up-forsale"
        else:
            ret["status"] = self.status
        return ret



    def xdetails(self):
        precision = 2
        trade_growth = trade_closed = trade_goal =  break_even = None
        #price = self.meta["details"].get("Limit",price)
        price = self.meta["details"].get("PricePerUnit",self.price)
        if price:
            trade_goal = round(price + ( price * self.increase_goal ) + comm,precision)
            break_even = price  + comm
            if self.status in ["done"]:
                sell_trade = self.meta.get("sell_trade_details",{})
                ret["assoc"] = sell_trade["id"]
                trade_closed = sell_trade.get("unitprice",trade_goal)
                if trade_closed is None or trade_closed == 0:
                    trade_closed = trade_goal

                trade_growth = round(((trade_closed- float(price)) / trade_closed) * 100,2)
            else:
                market_last = Exchange.getInstance().get_market_value(self.market)
                trade_growth = round(((market_last - float(price)) / market_last ) * 100,2)

        #ret["limit"] = self.meta["details"].get("Limit",self.price)
        ret["unitprice"] = price
        ret["commission"] = comm
        ret["breakeven"] = break_even
        ret["goal"] = trade_goal
        ret["soldat"] = trade_closed
        ret["change"] = "{}%".format(trade_growth)




        return ret

    def serialize(self):
        return {
                "id" : self.pkey,
                "exchange": self.exchange,
                "market": self.market,
                "quantity": self.quantity,
                "price": self.price,
                "trade_type": self.trade_type,
                "order_type": self.order_type,
                "created_by": self.created_by,
                "managed_by": self.managed_by,
                "status": self.status,
                "created_by": self.created_by,
                "active": self.active,
                "meta": json.dumps(self.meta,separators=(',',':'))
                }


    @staticmethod
    def load_by_id(val):
        pg = PgPool.getInstance()
        cur = pg.get_dict_cursor()
        cur.execute("""SELECT * FROM markets.trades WHERE id=%s """,[val])
        res = cur.fetchall()
        cur.close()

        newTrades = []
        for trade in res:
            newTrades += [Trade(trade)]


        return newTrades

    @staticmethod
    def load_by_status(status, active = True):
        pg = PgPool.getInstance()
        cur = pg.get_dict_cursor()
        cur.execute("""SELECT * FROM markets.trades WHERE active=%s and status=%s """,[active,status])
        res = cur.fetchall()
        cur.close()

        newTrades = []
        for trade in res:
            newTrades += [Trade(trade)]


        return newTrades

    @staticmethod
    def load_by_manager(manager, market, active = True):
        pg = PgPool.getInstance()
        cur = pg.get_dict_cursor()
        cur.execute("""SELECT * FROM markets.trades WHERE managed_by=%s and market=%s and active=%s """,[manager,market,active])
        res = cur.fetchall()
        cur.close()

        newTrades = []
        for trade in res:
            newTrades += [Trade(trade)]


        return newTrades



