class CoinCalc(object):

    _instance = None

    def __init__(self):
        self.last_prices  = {}

    def updatePrice(self, market, price ):
        self.last_prices[market] = price

    @staticmethod
    def getInstance():
        if CoinCalc._instance == None:
            CoinCalc._instance = CoinCalc()
        return CoinCalc._instance


    def get_market(self,currency):
        if currency.lower() == "usdt":
            market = "USDT-BTC"
        elif currency.lower() == "btc":
            market = "USDT-BTC"
        else:
            market = "BTC-{}".format(currency)

        return market

    def convert_usdt(self,currency,amount):
        if currency.lower() == "usdt":
            return amount
        else:
            market = self.get_market(currency)
            if market in self.last_prices:
                last = self.last_prices[market]
                return last * amount
            return 0


    def convert_btc(self,currency,amount):
        if currency.lower() == "btc":
            return amount
        else:
            market = self.get_market(currency)
            if market in self.last_prices:
                last = self.last_prices[market]
                if currency.lower() == "usdt":
                    return amount / last
                else:
                    return last * amount
            else:
                print("market {} not found".format(market))
                return 0



