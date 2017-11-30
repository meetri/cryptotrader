from result import Result

class ExchangeManager(object):

    def __init__(self, name, config = None):
        self.name = name
        if config is None:
            self.config = {
                    }
        else:
            self.config = config

    def processOrder(self, order ):
        return False

    def getName(self):
        return self.name


    def getOpenOrders(self):
        return False


    def getOrderById(self,extId):
        return False


    def placeOrder(self, order):
        return False


    def cancelOrder(self, order ):
        return False


    def cancelOrderById(self, extId):
        return False



