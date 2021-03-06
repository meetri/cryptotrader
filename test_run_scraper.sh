#!/bin/bash

while read line; do export $line; done < .env

DEBUGMODE=true \
GET_MARKET_SUMMARY=true \
GET_MARKET_ORDERS=false \
JOB=save_marketdata \
QUEUE=marketqueue \
MARKETLIST=USDT-BTC \
WORKERS=1 \
TA_WORKERS=0 \
INFLUXDB_HOST=localhost \
REDIS_HOST=localhost \
./src/scraper.py

