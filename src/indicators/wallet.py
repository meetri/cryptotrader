import os,sys,logging,decimal,time
import psycopg2.extras
from pgwrapper import PgPool
from exchange import Exchange
from bittrex import Bittrex

class Wallet(object):

    _instance = None

    def __init__(self):
        self.demo = False
        self.trades = []
        self.pgdb = None
        self.log = logging.getLogger('crypto')
        self.last_active_trade_query = 0
        self.bittrex_min_poll = 40


    @staticmethod
    def getInstance():
        if Wallet._instance == None:
            Wallet._instance = Wallet()

        return Wallet._instance


    #TODO: check exchange balance to see if I have funds. Also work on fund allocation for bots
    def buy_budget(self,market,amount):
        return True

    def getPgDb(self):
        if self.pgdb == None:
            self.pgdb = PgPool.getInstance()
        return self.pgdb


    def get_open_market_orders(self):
        pass
        #orders = Bittrex().

    def trade_sell(self, trade, price_exit ):

        conn = self.getPgDb().db.getconn()
        cur = conn.cursor(cursor_factory= psycopg2.extras.DictCursor )

        curval = Exchange.getInstance().get_market_value(trade["market"])
        if curval > price_exit:
            price_exit = curval

        res = Bittrex().market_selllimit( trade["market"], trade["trade_amount"], price_exit ).getData()
        self.log.info(res)
        if res["success"]:
            uuid = res["result"]["uuid"]
            cur.execute("""UPDATE markets.trades SET status=%s, trade_uuid=%s WHERE id=%s""",["selling",uuid,trade["id"],])
            res = conn.commit()

        self.getPgDb().db.putconn(conn)
        cur.close()


    def analyze_trade(self, idx ):
        goal_percent = decimal.Decimal(0.01)
        stoploss_percent = decimal.Decimal(0.5)

        if idx < len( self.trades ):

            t = self.trades[idx]
            precision = 2
            entry = t["price_entry"]
            trade_total = t["price_entry"] * t["trade_amount"]
            trade_fee = trade_total * t["market_fee"]
            break_even = t["price_entry"] + ( trade_fee )*2
            trade_goal = t["price_entry"] + ( t["price_entry"] * goal_percent ) + trade_fee

            stop_limit = t["price_entry"] - ( trade_total * decimal.Decimal(stoploss_percent) )

            market_last = Exchange.getInstance().get_market_value(t["market"])
            growth = ( decimal.Decimal((market_last - float(t["price_entry"])) / market_last)) * 100

            cur_market_value = Exchange.getInstance().get_market_value( t["market"] )

            if cur_market_value >= trade_goal and t["status"] == "active":
                self.trade_sell( t, trade_goal )

            return {
                    "m": t["market"],
                    "t":t["price_entry_date"],
                    "entry": round(entry,precision),
                    "amount": t["trade_amount"],
                    "total": round(trade_total,precision),
                    "growth": round(growth,precision),
                    "trade_fee": round(trade_fee,8),
                    "goal": round(trade_goal,precision),
                    "breakeven": round(break_even,precision),
                    "status": t["status"],
                    "limit": round(stop_limit,precision)
                    }


    def get_active_trades(self):
        if self.last_active_trade_query + self.bittrex_min_poll > time.time():
            return self.trades

        self.last_active_trade_query = time.time()
        conn = self.getPgDb().db.getconn()
        cur = conn.cursor(cursor_factory= psycopg2.extras.DictCursor )
        cur.execute("""select * from markets.trades WHERE active=true and status NOT IN ('closed','cancelled','sold') """)
        res = cur.fetchall()
        self.trades = res

        for trade in self.trades:
            uuid = trade["trade_uuid"]
            if len(uuid) >= 32 and trade["status"] in ["open","selling"]:
                self.log.info("getting order details from bittrex")
                trade_details = Bittrex().account_get_order(uuid).getData()
                if trade_details["result"]["IsOpen"] == False:
                    if trade["status"] == "open":
                        new_status = "active"
                    elif trade["status"] == "selling":
                        new_status = "sold"

                    cur.execute("""UPDATE markets.trades SET status=%s WHERE id=%s""",[new_status,trade["id"],])
                    res = conn.commit()
                    self.log.info(res)


        self.getPgDb().db.putconn(conn)
        cur.close()

        return self.trades


    def update_trade(self, trade ):
        pass

    def process_trade(self, signal ):
        precision = 2
        marketfee = 0.0025
        trade_amount = signal["trade_amount"]
        trade_total = round(signal["price_entry"] * trade_amount ,precision)
        trade_fee = round(trade_total * marketfee ,precision)

        uuid = None
        if not self.demo:
            res = Bittrex().market_buylimit(signal["market"],trade_amount,signal["price_entry"]).getData()
            self.log.info(res)
            if res["success"]:
                uuid = res["result"]["uuid"]
        else:
            uuid = "DEMO"

        if uuid is not None:
            data = {
                "exchange": signal["exchange"],
                "market": signal["market"],
                "price_entry": signal["price_entry"],
                "trade_amount": trade_amount,
                "trade_entry_total": trade_total,
                "price_entry_date": time.strftime("%c"),
                "trade_fee": trade_fee,
                "market_fee": marketfee,
                "trade_uuid": uuid,
                "status": "open"
                }
            self.log.info("saving to db")
            self.log.info(data)
            res =  self.new_trade(data)
        else:
            self.log.error("failed to add trade")

        #self.log.info("upgrade trade_id = {} price to {} from {}".format(trade_id,signal["price_entry"],signal["original_price"]))



    def manage_trade(self, bot ):
        data = bot.get_data()
        if data is not None and "result" in data:
            if data["result"]["details"]["signal"] == "oversold":
                reject = False
                try:
                    unmet_marketorders= 0
                    for trade_id in bot.botdata["bestbuy"]["processing"]:
                        unmet_marketorders += 1
                        trade = bot.botdata["bestbuy"]["processing"][trade_id]
                        if trade["price_entry"] > data["result"]["details"]["price_entry"]:
                            #self.log.info("replacing price_entry with unplaced trade")
                            #trade["details"]["price_entry"] = data["result"]["details"]["price_entry"]
                            reject = True

                    if unmet_marketorders == 0:
                        history = bot.botdata["bestbuy"]["history"]
                        for trade in history:
                            self.log.info("history {} == {}".format(data["result"]["cs_time"],trade["cs_time"]))
                            if trade["cs_time"] == data["result"]["cs_time"]:
                                reject = True
                                self.log.info("rejected - bot traded in this candlestick frame already")

                        if not reject:
                            bot.trade_executed()
                            bot.bestBuyBot(data["result"],self)
                            self.log.info("added trade to bustBuyBot trade manager")
                            return data["result"]

                    else:
                        self.log.info("rejected - there are unplaced trades for this bot")

                except Exception as ex:
                    self.log.error(ex)
                    pass







    def new_trade(self,trade ):
        obj = trade.copy ()
        obj["active"] = True
        res = self.getPgDb().insert("markets.trades",obj)
        self.log.info(res)
        trade["trade_id"] = res[0]
        return trade
