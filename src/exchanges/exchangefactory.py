from result import Result
from bittrexmanager import BittrexManager

class ExchangeFactory(object):

    @staticmethod
    def find(name):
        if name == "BTRX":
            return BittrexManager()

        return Result.fail("couldn't find exchange handler for {}".format(nameE))
