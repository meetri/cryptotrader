import sys,io

class Exchange(object):

    _instance = None

    def __init__(self):
        self.data = {}


    def get_market_value(self, market):
        if market in self.data:
            return self.data[market]
        else:
            return None


    def set_market_value(self, market, value ):
        self.data[market] = value


    @staticmethod
    def getInstance():
        if Exchange._instance == None:
            Exchange._instance = Exchange()
        return Exchange._instance


