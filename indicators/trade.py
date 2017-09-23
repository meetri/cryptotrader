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
        self.max_trade_quantity = 0.0001
        self.max_trade_frequency = 60    #seconds

        self.increase_goal = 0.02


    def sign_trade(self,trade):
        trade.meta["related_trade_id"] = self.pkey
        return trade


    def forsale(self,amount, minbuy=False):
        details = self.details()
        if self.trade_type == "buy" and self.status not in ["cancelled","closed","sold","new"]:
            if minbuy and details["breakeven"] <= amount:
                return True
            elif details["goal"] <= amount:
                return True



    def validate(self):
        if self.quantity > 0 and self.quantity <= self.max_trade_quantity:
            if len(self.market) > 0 and len(self.created_by) > 0 and len(self.managed_by) > 0:
                if self.trade_type in ["buy","sell"] and  self.order_type in ["limit","market","instant","demo","trailing"]:
                    if self.status in ["closed","new","buying","selling","sold","cancelled","holding","saving","open"]:
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

    def unserialize(self, tdata):
        self.pkey = tdata.get("id",None)
        self.market = tdata.get("market")
        self.exchange = tdata.get("exchange","bittrex")
        self.quantity = tdata.get("quantity")
        self.price = tdata.get("price")
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


    def details(self):

        if "details" in self.meta and self.meta["details"]:
            com = self.meta["details"].get("CommissionReserved")
        else:
            #self.log.info("missing details info in trade data")
            com = 0

        price = float(self.price)

        break_even = price  + ( com )*2
        trade_goal = price + ( price * self.increase_goal ) + (com*2)

        market_last = Exchange.getInstance().get_market_value(self.market)
        growth = round(((market_last - float(price)) / market_last ) * 100,2)

        ret = OrderedDict()
        ret["id"] = self.pkey
        ret["assoc"] = self.meta.get("related_trade_id")
        ret["market"] = self.market
        ret["order_type"] = self.order_type
        ret["trade_type"] = self.trade_type
        ret["qty"] = self.quantity
        ret["price"] = self.price
        ret["commission"] = com
        ret["breakeven"] = break_even
        ret["goal"] = trade_goal
        ret["change"] = "{}%".format(growth)
        ret["status"] = self.status
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
        conn = pg.db.getconn()
        cur = conn.cursor(cursor_factory= psycopg2.extras.DictCursor )
        cur.execute("""SELECT * FROM markets.trades WHERE id=%s """,[val])
        res = cur.fetchall()

        newTrades = []
        for trade in res:
            newTrades += [Trade(trade)]

        pg.db.putconn(conn)
        cur.close()

        return newTrades

    @staticmethod
    def load_by_status(status, active = True):
        pg = PgPool.getInstance()
        conn = pg.db.getconn()
        cur = conn.cursor(cursor_factory= psycopg2.extras.DictCursor )
        cur.execute("""SELECT * FROM markets.trades WHERE active=%s and status=%s """,[active,status])
        res = cur.fetchall()

        newTrades = []
        for trade in res:
            newTrades += [Trade(trade)]

        pg.db.putconn(conn)
        cur.close()

        return newTrades

    @staticmethod
    def load_by_manager(manager, active = True):
        pg = PgPool.getInstance()
        conn = pg.db.getconn()
        cur = conn.cursor(cursor_factory= psycopg2.extras.DictCursor )
        cur.execute("""SELECT * FROM markets.trades WHERE managed_by=%s and active=%s """,[manager,active])
        res = cur.fetchall()

        newTrades = []
        for trade in res:
            newTrades += [Trade(trade)]

        pg.db.putconn(conn)
        cur.close()

        return newTrades



