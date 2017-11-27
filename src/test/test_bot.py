#!/usr/bin/env python3.4
import unittest,time
import os,sys,logging,json

curdir = os.path.dirname(__file__)
sys.path.append( os.path.join(curdir, '../bots'))
sys.path.append( os.path.join(curdir, '../orders'))
sys.path.append( os.path.join(curdir, '../modules'))
sys.path.append( os.path.join(curdir, '../exchanges'))
sys.path.append( os.path.join(curdir, '../exchangeapis'))
sys.path.append( os.path.join(curdir, '../indicators'))
sys.path.append( os.path.join(curdir, '../datasources'))

logger = logging.getLogger('crypto')
hdlr = logging.FileHandler('/tmp/crypto-test.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)


from order import Order
from ordermanager import OrderManager
from bittrexmanager import BittrexManager
from simplesurfer import SimpleSurfer

class TestExchange(unittest.TestCase):

    @unittest.skip("manual test.")
    def test_exchange_order_details(self):
        mybot = SimpleSurfer("USDT-BTC")
        mybot.process()

        res = mybot.dataProvider().getInfo("details")
        print(res)

    @unittest.skip("manual test.")
    def test_bot_signal(self):
        st = time.time()
        bot = SimpleSurfer("BTC-POWR",0.001,5,"5m","24h")
        bot.pushSignal("bband","buy",10)
        sig = bot.getSignal()
        self.assertTrue(sig.get("name") == "SimpleSurfer")
        self.assertTrue(sig.get("signal") == "buy")
        self.assertTrue(sig.get("strength") == 10)
        self.assertTrue(sig.get("time") >= st)


    @unittest.skip("manual test.")
    def test_order_gen(self):
        st = time.time()
        bot = SimpleSurfer("BTC-POWR",0.005,2,"5m","24h")
        bot.pushSignal("bband","buy",10)
        if bot.getSignal():
            orderman = OrderManager( BittrexManager() )
            order = orderman.botSignal( bot )
            if order:
                res = orderman.send(order)
                print(res)


    @unittest.skip("manual test.")
    def test_order_sync(self):
        st = time.time()
        bot = SimpleSurfer("BTC-POWR",0.005,2,"5m","24h")
        orderman = OrderManager( BittrexManager() )
        orderman.syncOpenOrders(bot)


    @unittest.skip("manual test.")
    def test_trade_list(self):
        st = time.time()
        bot = SimpleSurfer("BTC-POWR",0.005,2,"5m","24h")
        orderman = OrderManager( BittrexManager() )
        bot.setOrderManager(orderman)
        trades = bot.dataProvider().get_trades()
        print(trades)


    @unittest.skip("manual test.")
    def test_trade_sell(self):
        bot = SimpleSurfer({
            "market":"BTC-POWR",
            "candlestick": "5m",
            "budget": 0.005,
            "tradelimit": 2
            })

        orderman = OrderManager( BittrexManager() )
        bot.setOrderManager(orderman)
        bot.pushSignal("test","sell",50)
        bot.growth_target = -1
        bot.getOrderManager().processSignal()


    def test_order_sync2(self):
        bot = SimpleSurfer({
            "market":"BTC-POWR",
            "candlestick": "5m",
            "budget": 0.005,
            "tradelimit": 2
            })

        orderman = OrderManager( BittrexManager() )
        bot.setOrderManager(orderman)
        bot.getOrderManager().syncOpenOrders()


if __name__ == '__main__':
    unittest.main()
