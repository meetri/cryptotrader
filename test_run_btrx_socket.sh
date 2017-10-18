#!/bin/bash

while read line; do export $line; done < .env

DEBUGMODE=true \
GET_MARKET_SUMMARY=false \
GET_MARKET_ORDERS=true \
MARKET_LIST="USDT-BTC USDT-ETH USDT-LTC" \
PGUSER=postgres \
PGDATABASE=crypto \
REDIS_HOST=localhost \
REDIS_PORT=6379 \
node ./src/nodejs/scrapeall.js

