import os,sys,talib,numpy,logging
from collections import OrderedDict
from influxdbwrapper import InfluxDbWrapper
from tools import Tools
from bittrex import Bittrex
from trader import Trader
from coincalc import CoinCalc
from technicalanalyzer import TechnicalAnalyzer

"""
from macd import MACD
from bollingerbands import BBands
from atr import ATR
from sma import SMA
from rsi import RSI
"""

class Analyzer(object):

    def __init__(self, csdata ):
        self.log = logging.getLogger('crypto')

        #a list of indicators used validate trade positions
        self.indicators = []

        #in memory data store for each market's analysis
        self.datastore = {}

        #candlestick chart data
        self.cs = csdata
        self.ta = TechnicalAnalyzer(self)

        self.options = {}

        self.backtest_timeindex = 0


    def getIndicators(self):
        return self.indicators

    def last( self, datapoint, index = 1 ):
        return self.cs[datapoint][-1*index]

    def getIndicator(self,indicator):
        for i in range(0,len(self.indicators)):
            if self.indicators[i]["label"] == indicator:
                return self.indicators[i]["object"]


    def addIndicator(self, indicator, options = {}, label = None ):
        if label is None:
            label = indicator

        label = options["label"] = options.get("label",label)
        self.indicators += [{"indicator":indicator,"label":label,"options":options,"object":None}]


    #TODO remove...
    def add_indicator(self, indicator, options = {}, label = None ):
        return self.addIndicator(indicator,options,label)

    def saveIndicator(self, label, indicator ):
        self.indicators += [{"label":label,"object":indicator}]


    def process(self):
        ret ={}
        for indicatorObj in self.indicators:
            if "object" not in indicatorObj:
                indicator = indicatorObj.get("indicator")
                label = indicatorObj.get("label")
                options = indicatorObj.get("options",{})

                if label is None or len(label) == 0:
                    label = indicator

                indicator_class = Tools.loadClass(indicator)
                if indicator_class:
                    indicator_obj = indicator_class( self.cs, options )

                    indicatorObj["object"] = indicator_obj
                    ret[label] = indicator_obj.get_analysis()
                else:
                    raise Exception("Problem instantiating indicator {}".format(label))


        return ret
