#!/usr/bin/env python3.4
import os,sys,time,curses
import logging
import json
import cryptolib

from columnize import Columnize
from exman import ExchangeManager
from trade import Trade

exman = ExchangeManager()
logger = logging.getLogger('crypto')

def draw_results( stdscr, rows ):
    stdscr.clear()
    Columnize.cursesMultiMap(stdscr,0, rows )
    stdscr.refresh()


def main(stdscr):
    while True:
        trades = Trade.load_by_status("cancelled")
        rows = []
        for trade in trades:
            rows += [ trade.details() ]

        if len(rows) > 0:
            draw_results(stdscr,rows)

        time.sleep(5)

curses.wrapper(main)
