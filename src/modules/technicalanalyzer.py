from ema import EMA
from rsi import RSI
from macd import MACD
from sma import SMA
from atr import ATR
from bbands import BBands
from doubleband import DoubleBand

class TechnicalAnalyzer(object):

    def __init__(self, analyzer ):

        self.analyzer = analyzer
        self.csdata = analyzer.cs


    def getema(self,period = 14,label="ema"):
        tag = "ema:{}".format(period)
        ema = self.analyzer.findIndicator(tag)
        if not ema:
            ema = EMA(self.csdata,{"period":period},label)
            self.analyzer.saveIndicator(tag,ema)
        return ema


    def ema(self, period = 14,label="ema" ):
        return self.getema(period,label).data[-1]


    def getsma(self,period = 14,label="sma"):
        tag = "sma:{}".format(period)
        sma = self.analyzer.findIndicator(tag)
        if not sma:
            sma = SMA(self.csdata,{"period":period,"label":label})
            self.analyzer.saveIndicator(tag,sma)
        return sma


    def sma(self, period = 14,label="sma" ):
        return self.getsma(period).data[-1]


    def getatr(self,period = 14,label="atr"):
        tag = "atr:{}".format(period)
        ind = self.analyzer.getIndicator(tag)
        if not ind:
            ind = SMA(self.csdata,{"period":period,"label":label})
            self.analyzer.saveIndicator(tag,ind)
        return ind


    def atr(self, period = 14,label="atr" ):
        return self.getatr(14).data[-1]


    def getrsi(self,period = 14,label="rsi"):
        tag = "rsi:{}".format(period)
        ind = self.analyzer.getIndicator(tag)
        if not ind:
            ind = RSI(self.csdata,{"period":period,"label":label})
            self.analyzer.saveIndicator(tag,ind)
        return ind


    def rsi(self, period = 14,label="rsi" ):
        return self.getrsi(14).data[-1]


    def dband(self,period,stdev1,stdev2,label="bband"):
        b1 = self.getbband(period,stdev1,stdev1,label="bband")
        b2 = self.getbband(period,stdev2,stdev2,label="ibband")
        return DoubleBand(self.analyzer, outer=b1,inner=b2)


    def getbband(self, period = 14, nbdevup=2, nbdevdn=2, matype=0,label="bband" ):
        tag = "bband:{}:{}:{}:{}".format(period,nbdevup,nbdevdn,matype)
        ind = self.analyzer.getIndicator(tag)
        if not ind:
            ind = BBands(self.csdata,{"timeperiod":period,"nbdevup":nbdevup,"nbdevdn":nbdevdn,"matype":matype,"label":label})
            self.analyzer.saveIndicator(tag,ind)
        return ind


    def getmacd(self, fastperiod=12, slowperiod=26, signalperiod=9,label="macd" ):
        tag = "macd:{}:{}:{}:{}".format(fastperiod,slowperiod,signalperiod)
        ind = self.analyzer.getIndicator(tag)
        if not ind:
            ind = MACD(self.csdata,{"fastperiod":fastperiod,"slowperiod":slowperiod,"signalperiod":signalperiod,"label":label})
            self.analyzer.saveIndicator(tag,ind)
        return ind
