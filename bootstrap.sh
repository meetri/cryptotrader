#!/bin/bash

export JOB=${JOB:-"scraper"}
export PGUSER=${PGUSER:-"postgres"}
export PGPASSWORD=${PGPASSWORD:-"helloworld"}
export PGDATABASE=${PGDATABASE:-"crypto"}

if [ $JOB = "nodejs_websocket" ];then
    exec /usr/bin/node /opt/crypto/nodejs/scrapeall.js
else 
    exec /usr/bin/python3.4 -u /opt/crypto/scraper.py
fi
