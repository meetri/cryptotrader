#!/usr/bin/env python3.4
import unittest
import os,sys,logging,json

curdir = os.path.dirname(__file__)
sys.path.append( os.path.join(curdir, '../orders'))
sys.path.append( os.path.join(curdir, '../modules'))
sys.path.append( os.path.join(curdir, '../exchanges'))
sys.path.append( os.path.join(curdir, '../exchangeapis'))

from order import Order
from ordermanager import OrderManager
from bittrexmanager import BittrexManager

class TestExchange(unittest.TestCase):

    @unittest.skip("manual test.")
    def test_insufficient_funds(self):

        om = OrderManager( BittrexManager(), {} )
        order = Order.create ({
            "order_type": Order.BUY,
            "market": "USDT-BTC",
            "qty": 500,
            "rate": 1000.00
        })

        self.assertTrue( order.order_type == Order.BUY )
        self.assertTrue( order.qty == 0.001 )
        self.assertTrue( order.rate == 7000.00)


    @unittest.skip("manual test.")
    def test_create_order(self):
        om = OrderManager( BittrexManager(), {} )
        order = Order.create ({
            "order_type": Order.BUY,
            "market": "USDT-BTC",
            "qty": 0.001,
            "rate": 7000.00
        })

        self.assertTrue( order.order_type == Order.BUY )
        self.assertTrue( order.qty == 0.001 )
        self.assertTrue( order.rate == 7000.00)
        #res = om.send( order )
        #print(res)


    @unittest.skip("manual test.")
    def test_exchange_order_details(self):
        src = Order.findById(6)
        self.assertTrue ( src.data["found"] > 0 )

        order = src.data["results"][0]
        info = order.getExchangeManager().getOrderInfo(order)
        self.assertTrue( info["success"] == True )
        self.assertTrue( info["result"]["Type"] == "LIMIT_BUY")

        order.meta["api"].append ( info )
        res = order.save()
        print(res)



if __name__ == '__main__':
    unittest.main()
