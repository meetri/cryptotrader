#!/bin/bash

export JOB=${JOB:-""}
export PGUSER=${PGUSER:-"postgres"}
export PGPASSWORD=${PGPASSWORD:-"helloworld"}
export PGDATABASE=${PGDATABASE:-"crypto"}

if [ ${#JOB} -eq 0 ]; then
    echo "devmode"
    sleep infinity
elif [ $JOB = "nodejs_websocket" ]; then
    exec /usr/bin/node /opt/crypto/nodejs/scrapeall.js
else 
    exec /usr/bin/python3.4 -u /opt/crypto/scraper.py
fi
