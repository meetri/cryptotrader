#!/usr/bin/env python3.4

import os,sys,time,curses,logging,cryptolib

from influxdbwrapper import InfluxDbWrapper
from bottools import BotTools


db = InfluxDbWrapper.getInstance()

def getGrowth(market,dur="5m"):
   global db

   query = """SELECT FIRST(last) as last, LAST(last) as cur, 10000 * (LAST(last)-FIRST(last)) / (FIRST(last) * 100)  as p3 FROM "market_summary" WHERE marketname='{}' AND time > now() - {} ORDER by time asc""".format(market,dur)

   res = db.raw_query(query)
   for data in res:
       return data[0]


threshold = 10;

marketlist = db.raw_query("""SHOW TAG VALUES WITH KEY = {}""".format("marketname"))

while True:
    f = {}
    print("--")
    for markets in marketlist:
        for market in markets:
            if market["value"] not in f:
                f[market["value"]] = True
                growth = getGrowth(market["value"])
                if growth:
                    if abs(growth["p3"]) > threshold:
                        print("{}: {}% ( {} - {} )".format(market["value"], growth["p3"],growth["last"],growth["cur"]))
    time.sleep(10)
