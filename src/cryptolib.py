#!/usr/bin/env python3.4
"""
scrape jobs retrieved from queue
"""

import os,sys,logging

curdir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(curdir + "/modules")
sys.path.append(curdir + "/datasources")
sys.path.append(curdir + "/exchangeapis")
sys.path.append(curdir + "/indicators")
sys.path.append(curdir + "/bots")
sys.path.append(curdir + "/orders")
sys.path.append(curdir + "/exchanges")

logger = logging.getLogger('crypto')
hdlr = logging.FileHandler('/tmp/crypto.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)

