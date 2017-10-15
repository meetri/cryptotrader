#!/usr/local/bin/python3 -u
"""
scrape jobs retrieved from queue
"""

import os,sys,time,redis,json
import concurrent.futures

curdir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(curdir + "/modules")
sys.path.append(curdir + "/indicators")
sys.path.append(curdir + "/datasources")
sys.path.append(curdir + "/exchangeapis")

from exchangedata import ExchangeDataHandler
from influxdbwrapper import InfluxDbWrapper
from coincalc import CoinCalc
from trader import Trader

ta_workers = int(os.getenv("TA_WORKERS","5"))
if ta_workers > 0:
    # add ta worker for orchestration
    ta_workers += 1

save_workers = int(os.getenv("WORKERS","10"))
worker_threads = ta_workers + save_workers
read_queue  = os.getenv("QUEUE","marketqueue")
influxDb = InfluxDbWrapper.getInstance()

market_list = os.getenv("MARKETLIST","")
frame_sizes = os.getenv("FRAMESIZES","1m 5m 15m")

if len(market_list) == 0:
    market_list = ExchangeDataHandler().getInstance().getMarketList(0,500)


def ta_orchestrator():
    global market_list
    redis = ExchangeDataHandler().getInstance().getRedisDb()
    starttime = 0
    diftime = 0
    while True:
        try:
            if redis.llen("ta_markets") == 0:
                if starttime > 0:
                    diftime = time.time() - starttime
                    print("completed ta cycle in {} seconds".format(diftime))
                for market in market_list.split(" "):
                    redis.rpush("ta_markets",market)
                starttime = time.time()
            else:
                time.sleep(5)

        except Exception as ex:
            print("push_ta_queue exception thrown: {}".format(ex))


def market_tadata(worker_id):
    global influxDb

    while True:
        try:
            res = ExchangeDataHandler().getInstance().getRedisDb().blpop("ta_markets")
            market = res[1].decode("utf-8")
            received_ts = time.strftime("%c")
            for framesize in frame_sizes.split(" "):
                starttime = time.time()
                traderTA = Trader(market)
                cs  = traderTA.get_candlesticks("24h",framesize)
                traderTA.get_indicators()
                endtime = time.time()
                diftime = endtime - starttime
                #print("TA on {} with {} framesize completed in {}".format(market,framesize,diftime))
                for i in range(0,traderTA.get_indicator_size()):
                    res = traderTA.get_indicator_index(i)
                    influxDb.bulkAddTA("bittrex",traderTA.market,framesize,res,diftime)

        except Exception as ex:
            print("market_tadata exception thrown: {}".format(ex))


def scrape_marketdata(worker_id):
    global influxDb
    global read_queue

    while True:
        try:
            res = ExchangeDataHandler().getInstance().getRedisDb().blpop(read_queue)
            data = json.loads ( res[1].decode("utf-8"))
            received_ts = time.strftime("%c")

            if "M" in data and "A" in data:

                if data["M"] == "account":
                    for account in data["A"]:
                        account["TimeStamp"] = received_ts
                        influxDb.bulkAddAccountDetails("bittrex",account)
                elif data["M"] == "updateSummaryState":
                    for delta in data["A"][0]["Deltas"]:
                        CoinCalc.getInstance().updatePrice(delta["MarketName"],delta["Last"])
                        influxDb.bulkAddMarketSummary("bittrex",delta)
                elif data["M"] == "updateExchangeState":
                    nonce = data["A"][0]["Nounce"]
                    marketname = data["A"][0]["MarketName"]
                    for item in data["A"][0]["Sells"]:
                        item["MarketName"] = marketname
                        item["OrderType"] = "SELL"
                        item["TimeStamp"] = item["Received"] = received_ts
                        influxDb.bulkAddExchangeState("bittrex",nonce,False,item)
                    for item in data["A"][0]["Buys"]:
                        item["MarketName"] = marketname
                        item["OrderType"] = "BUY"
                        item["TimeStamp"] = item["Received"] = received_ts
                        influxDb.bulkAddExchangeState("bittrex",nonce,False,item)
                    for item in data["A"][0]["Fills"]:
                        item["Type"] = 0
                        item["MarketName"] = marketname
                        item["Received"] = received_ts
                        influxDb.bulkAddExchangeState("bittrex",nonce,True,item)
                else:
                    print("Unhandled message: {}".format(data["M"]))
                    print(data)

        except Exception as ex:
            print ("exception captured: {}".format(ex))


queue_futures = []
with concurrent.futures.ThreadPoolExecutor(max_workers=worker_threads) as executor:
    for worker_idx in range(1,worker_threads+1):
        if worker_idx <= ta_workers:
            if worker_idx == 1:
                print("worker {} created for TA Analysis orchestration".format(worker_idx))
                queue_futures.extend([executor.submit(ta_orchestrator)])
            else:
                print("worker {} created for TA Analysis".format(worker_idx))
                queue_futures.extend([executor.submit(market_tadata,worker_idx)])
        else:
            print("worker {} created for saving market data".format(worker_idx))
            queue_futures.extend([executor.submit(scrape_marketdata,worker_idx)])

    for future in concurrent.futures.as_completed(queue_futures):
        print("ERROR: market queue thread exited")

print('bye')
