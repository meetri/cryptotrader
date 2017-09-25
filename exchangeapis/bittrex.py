import time
import math
import hashlib
import hmac
import json
import os
import requests

class Bittrex(object):

    def __init__(self, key = None,secret = None):
        self.timeout = 4
        self.api_root = "https://bittrex.com/api/v1.1/"
        self.api2_root = "https://bittrex.com/Api/v2.0/"
        if key == None:
            self.api_key = os.getenv("bittrex_key","")
            self.api_secret = os.getenv("bittrex_secret","")
        else:
            self.api_key = key
            self.api_secret = secret

        self.response = None
        self.data = None

        self.headers = {
            "Content-Type": "application/json",
        }


    def process(self, api_path, payload = {}):

        appendchar = "?"
        if appendchar in api_path:
            appendchar = "&"

        nonce = time.time()
        uri = "{}{}{}".format(self.api_root,api_path,appendchar)
        apisign = hmac.new ( self.api_secret.encode(), uri.encode(), hashlib.sha512 ).hexdigest()
        self.headers["apisign"] = apisign

        self.response = requests.post( uri , data = json.dumps(payload) , headers = self.headers, timeout=self.timeout )
        self.response.raise_for_status()
        self.data = self.response.json()

        return self

    def private_process(self, api_path, payload = {}):

        appendchar = "?"
        if appendchar in api_path:
            appendchar = "&"

        nonce = math.floor(time.time())
        uri = "{}{}{}apikey={}&nonce={}".format(self.api_root,api_path,appendchar,self.api_key,nonce)
        apisign = hmac.new ( self.api_secret.encode(), uri.encode(), hashlib.sha512 ).hexdigest()
        self.headers["apisign"] = apisign

        self.response = requests.post( uri , data = json.dumps(payload) , headers = self.headers, timeout=self.timeout )
        self.response.raise_for_status()
        self.data = self.response.json()

        return self

    def private_process2(self, api_path, payload = {}):

        appendchar = "?"
        if appendchar in api_path:
            appendchar = "&"

        nonce = math.floor(time.time())
        uri = "{}{}{}apikey={}&nonce={}".format(self.api2_root,api_path,appendchar,self.api_key,nonce)
        print(uri)
        print(json.dumps(payload))
        apisign = hmac.new ( self.api_secret.encode(), uri.encode(), hashlib.sha512 ).hexdigest()
        self.headers["apisign"] = apisign

        self.response = requests.post( uri , data = json.dumps(payload) , headers = self.headers, timeout=self.timeout )
        self.response.raise_for_status()
        if self.response is not None:
            self.data = self.response.json()

        return self

    def process2(self, api_path, payload = {}):

        appendchar = "?"
        if appendchar in api_path:
            appendchar = "&"

        nonce = time.time()
        #uri = "{}{}{}".format(self.api2_root,api_path,appendchar)
        uri = "{}{}".format(self.api2_root,api_path)
        apisign = hmac.new ( self.api_secret.encode(), uri.encode(), hashlib.sha512 ).hexdigest()
        self.headers["apisign"] = apisign

        self.response = requests.post( uri , data = json.dumps(payload) , headers = self.headers, timeout=self.timeout )
        self.response.raise_for_status()
        if self.response is not None:
            self.data = self.response.json()

        return self

    def getData(self):
        return self.data

    #api v2.0
    def public_get_candles(self,market="USDT-BTC",tickInterval="fiveMin",starttime=None):
        if starttime is None:
            starttime = int(time.time())
        return self.private_process2("pub/market/GetTicks?marketName={}&tickInterval={}&_={}".format(market,tickInterval,int(starttime)))

    def market2_tradebuy( self, market,qty,rate, ordertype="LIMIT",timeineffect="IMMEDIATE_OR_CANCEL",condition="NONE",target=0):
        #TimeInEffect: 'IMMEDIATE_OR_CANCEL', // supported options are 'IMMEDIATE_OR_CANCEL', 'GOOD_TIL_CANCELLED', 'FILL_OR_KILL'
        #ConditionType: 'NONE', // supported options are 'NONE', 'GREATER_THAN', 'LESS_THAN'
        return self.private_process2("key/market/TradeBuy?MarketName={}&OrderType={}&Quantity={}&Rate={}&TimeInEffect={}&Condition={}&Target={}".format(market,ordertype,qty,rate,timeineffect,condition,target))
        #return self.private_process2("key/market/TradeBuy?MarketName={}&OrderType={}&Quantity={}&Rate={}&TimeInEffect={}&Condition={}&Target={}".format(market,ordertype,qty,rate,timeineffect,condition,target))
        #return self.private_process2("key/market/TradeBuy".format(market,ordertype,qty,rate,timeineffect,condition,target),options)

    #api v1.1
    def public_get_markets(self):
        return self.process("public/getmarkets")

    def public_get_market(self,market):
        return self.process("public/getmarket?market={}".format(market))

    def public_get_currencies(self):
        return self.process("public/getcurrencies")

    def public_get_ticker(self,market):
        return self.process("public/getticker?market={}".format(market))

    def public_get_market_summaries(self):
        return self.process("public/getmarketsummaries")

    def public_get_market_summary(self, market ):
        return self.process("public/getmarketsummary?market={}".format(market))

    def public_get_orderbook(self, market, obType="both" ):
        return self.process("public/getorderbook?market={}&type={}".format(market,obType))

    def public_get_market_history(self, market ):
        return self.process("public/getmarkethistory?market={}".format(market))

    def market_buylimit( self, market, quantity, rate ):
        return self.private_process("market/buylimit?market={}&quantity={}&rate={}".format(market,quantity,rate))

    def market_selllimit( self, market, quantity, rate ):
        return self.private_process("market/selllimit?market={}&quantity={}&rate={}".format(market,quantity,rate))

    #undocumented / disabled ====
    def market_sellmarket( self, market, quantity):
        return self.private_process("market/sellmarket?market={}&quantity={}&rate={}".format(market,quantity))
    def market_buymarket( self, market, quantity):
        return self.private_process("market/buymarket?market={}&quantity={}".format(market,quantity))
    #=========================

    def market_cancel( self, uuid ):
        return self.private_process("market/cancel?uuid={}".format(uuid))

    def market_get_open_orders( self, market):
        return self.private_process("market/getopenorders?market={}".format(market))

    def account_get_order( self, uuid ):
        return self.private_process("account/getorder?uuid={}".format(uuid))

    def account_get_balances( self ):
        return self.private_process("account/getbalances")

    def account_get_balances( self ):
        return self.private_process("account/getbalances")

