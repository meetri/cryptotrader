from ema import EMA
from sma import SMA
from atr import ATR
from bbands import BBands

class TechnicalAnalyzer(object):

    def __init__(self, candlestick_data ):
        self.csdata = candlestick_data

    def ema(self, period = 14 ):
        return EMA(self.csdata,{"period":period}).data[-1]

    def sma(self, period = 14 ):
        return SMA(self.csdata,{"period":period}).data[-1]

    def atr(self, period = 14 ):
        return ATR(self.csdata,{"period":period}).data[-1]

    def getBBand(self, period = 14, nbdevup=2, nbdevdn=2, matype=0 ):
        return BBands(self.csdata,{"timeperiod":period,"nbdevup":nbdevup,"nbdevdn":nbdevdn,"matype":matype})

