import json
import psycopg2.extras

from result import Result
from pgwrapper import PgPool
from tools import Tools

class Order(object):

    OPEN = 100
    CANCELLED = 200
    PARTIAL_FILL = 300
    FILLED = 301

    TERMINATED_STATE = 350

    UPFORSALE = 390
    COMPLETED = 400
    ERROR = 900

    MARKET = 0
    BUY = 1
    SELL = 2

    DUST  = .0001

    TYPES = {SELL:"sell",BUY:"buy"}
    STATUS = {OPEN:"open",CANCELLED:"cancelled",PARTIAL_FILL:"partial fill",FILLED:"filled",UPFORSALE:"upforsale",COMPLETED:"completed",ERROR:"error"}


    def __init__(self, orderInfo = None ) :
        self.pgpool = PgPool.getInstance()

        self.pkey = None

        #exchange order id
        self.ref_id = None

        #id this trade is associated with
        self.assoc_id = None

        self.order_type = None
        self.created_by = None
        self.created_ts = None
        self.exchange = None
        self.market = None
        self.rate = 0
        self.qty = 0
        self.status = 0

        self.meta = {}

        #temp data
        self.upforsale = None

        if orderInfo is not None:
            self.dbdata = orderInfo
            self.deserialize(orderInfo)


    def __str__(self):
        return json.dumps(self.serialize())


    @staticmethod
    def create(data):
        return Order(data)


    def getView(self, lastrate = None):
        ot = Order.TYPES
        os = Order.STATUS

        growth = ""
        profit = 0
        if self.order_type == Order.BUY:

            if self.status == Order.COMPLETED:
                lastrate = self.meta["sold_at"]

            if self.status == Order.FILLED or self.status == Order.COMPLETED:
                growth = "{:.02f}".format(Tools.calculateGrowth(lastrate,self.rate))

                if self.status == Order.COMPLETED:
                    profit = ( float(self.qty) * float(lastrate)) - ( float(self.qty) * float(self.rate) )
                    #profit = "{:.08f}".format(profit)


        if growth:
            growth = float(growth)
        else:
            growth = 0

        res = {
                "id": self.pkey,
                "order_type": ot[ self.order_type ],
                "qty": "{:.08f}".format(self.qty),
                "rate": "{:.08f}".format(self.rate),
                "growth": growth,
                "profit": profit,
                "status": os[self.status],
                "time": self.created_ts,
                "candle_time": self.meta["candle_trade_time"]
                }

        if self.order_type == Order.BUY and self.status == Order.COMPLETED:
            res["sold_at"] = "{:.08f}".format(lastrate)

        return res


    def serialize(self):
        data = {
            "ref_id": self.ref_id,
            "assoc_id": self.assoc_id,
            "order_type": self.order_type,
            "created_by": self.created_by,
            "exchange": self.exchange,
            "market": self.market,
            "qty": self.qty,
            "rate": self.rate,
            "status": self.status,
            "meta": json.dumps(self.meta,separators=(',',':'))
            }

        if self.pkey:
            data["id"] = self.pkey

        return data


    def deserialize(self, data ):
        self.pkey  = data.get("id",self.pkey)
        self.ref_id = data.get("ref_id",self.ref_id)
        self.assoc_id = data.get("assoc_id",self.ref_id)
        self.created_by = data.get("created_by",self.created_by)
        self.order_type = int(data.get("order_type",self.order_type))
        self.exchange = data.get("exchange",self.exchange)
        self.market = data.get("market",self.market)
        self.rate  = data.get("rate",self.rate)
        self.qty  = data.get("qty",self.qty)
        self.status = int(data.get("status",self.status))
        if data.get("created_ts"):
            self.created_ts = data.get("created_ts").timestamp()

        if data.get("upforsale"):
            self.upforsale = data["upforsale"]

        self.meta = data.get("meta",self.meta)
        if "candle_time" in data and data["candle_time"] is not None:
            self.meta["candle_trade_time"]  = data["candle_time"]


    def _insert(self):
        ser = self.serialize()
        res = self.pgpool.insert("markets.orders", ser )
        if res and res > 0:
            self.pkey = res
        return res


    def _update(self):
        data = self.serialize()
        if "id" in data:
            return self.pgpool.update("markets.orders","id", data, self.dbdata)


    def save(self):
        if self.dbdata and self.pkey:
            r = self._update()
            if r and r > 0:
                return Result.success(data={ "action":"updated","rows_updated": r } )
            else:
                return Result.fail("unable to update",data={ "results": r })
        else:
            r = self._insert()
            if r and r > 0:
                return Result.success(data={ "action":"inserted","insert_id": r } )
            else:
                return Result.fail("unable to insert")


    @staticmethod
    def findByBot(botname,market,exchange):
        orders = []
        res = PgPool.getInstance().select("""SELECT * FROM markets.orders WHERE created_by=%s AND market=%s AND exchange=%s""",[botname,market,exchange])
        for order in res:
            orders .append( Order.create(order) )

        return Result( len(orders) > 0, data = { "found": len(orders),"results": orders } )

    @staticmethod
    def findByBotStatus(botname,market,status):
        orders = []
        res = PgPool.getInstance().select("""SELECT * FROM markets.orders WHERE created_by=%s AND market=%s AND status=%s""",[botname,market,status])
        for order in res:
            orders .append( Order.create(order) )

        return Result( len(orders) > 0, data = { "found": len(orders),"results": orders } )

    @staticmethod
    def findByBotActive(botname,market,exchange):
        orders = []
        res = PgPool.getInstance().select("""SELECT * FROM markets.orders WHERE created_by=%s AND market=%s AND exchange=%s AND status < %s""",[botname,market,exchange,Order.COMPLETED])
        for order in res:
            orders .append( Order.create(order) )

        return Result( len(orders) > 0, data = { "found": len(orders),"results": orders } )

    @staticmethod
    def findById(val):
        orders = []
        res = PgPool.getInstance().select("""SELECT * FROM markets.orders WHERE id=%s """,[val])
        for order in res:
            orders .append( Order.create(order) )


        return Result( len(orders) > 0, data = { "found": len(orders),"results": orders } )


    @staticmethod
    def findAll(val):
        orders = []
        res = PgPool.getInstance().select("""SELECT * FROM markets.orders WHERE not disabled and status!=%s""",[Order.COMPLETED])
        for order in res:
            orders .append( Order.create(order) )

        return Result( len(orders) > 0, data = { "found": len(orders),"results": orders } )


    def setExchange(self,exchange):
        self.exchange = exchange


    @staticmethod
    def sumOrders(orders):
        total = 0
        for order in orders:
            if order.status > 0 and order.status < Order.COMPLETED:
                total += order.qty * order.rate

        return total
