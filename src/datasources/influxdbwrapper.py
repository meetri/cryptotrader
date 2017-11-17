import os,sys,time

from influxdb import InfluxDBClient
from threading import Lock
from coincalc import CoinCalc


class InfluxDbWrapper(object):

    _instance = None

    def __init__(self):
        #print("init influxdb")
        self.min_save_interval = 1
        self.last_save_time = 0

        args = {
                "host": os.getenv("INFLUXDB_HOST","localhost"),
                "port": int(os.getenv("INFLUXDB_PORT","8086")),
                "database": os.getenv("INFLUXDB_DBNAME","crypto")
                }
        self.influxdb = InfluxDBClient(**args)

        self.data = {
                "marketdata" : [],
                }

        self.influx_bulk_lock = {
                "marketdata" : Lock(),
                }

    def getInfluxDb(self):
        return self.influxdb


    @staticmethod
    def getInstance():
        if InfluxDbWrapper._instance is None:
            InfluxDbWrapper._instance = InfluxDbWrapper()
        return InfluxDbWrapper._instance

    def raw_query(self,query ):
        res = self.influxdb.query( query )
        return res

    def getBulkSize(self,group="marketdata"):
        return len(self.data[group])

    def bulkSave(self, group="marketdata" ):

        if len(self.data[group]) > 0:
            with self.influx_bulk_lock[group]:
                influx_data = self.data[group].copy()
                del self.data[group][:len(influx_data)]

            self.last_save_time = time.time()
            print("sending {} bulk elements to influxdb".format(len(influx_data)))
            try:
                inf_res = self.getInfluxDb().write_points( influx_data )
                if not inf_res:
                    print("problem writing {} to influxdb".format(market))
            except Exception as ex:
                print("influxdb Exception: {}".format(type(ex)))
                raise

    def bulkAdd(self,item,group="marketdata"):
        self.data[group].extend([item])
        bulkAutoSaveCount = int(os.getenv("INFLUXDB_BULKSAVECOUNT","500"))
        if self.getBulkSize() > bulkAutoSaveCount or time.time()-self.min_save_interval > self.last_save_time:
            self.bulkSave(group)

    def bulkAddAccountDetails(self,exchange,account):

        if account["Available"] > 0:
            marketpair = CoinCalc.getInstance().get_market( account["Currency"] )
            btc_value = CoinCalc.getInstance().convert_btc( account["Currency"], account["Available"] )
            usdt_value = CoinCalc.getInstance().convert_usdt( account["Currency"], account["Available"] )

            item = {
                        "measurement": "crypto_holdings",
                        "tags": {
                            "currency": account["Currency"],
                            "market": marketpair,
                            "exchange": exchange
                            },
                        "fields": {
                            "balance": float(account["Balance"]),
                            "available": float(account["Available"]),
                            "pending": float(account["Pending"]),
                            "btc_estimate_value": float(btc_value),
                            "usdt_estimate_value": float(usdt_value)
                            }
                        }
            self.bulkAdd(item)


    def bulkAddExchangeState(self,exchange,nounce,fillorder,row):
        self.bulkAdd({
            "measurement": "market_history",
            "tags": {
                "marketname": row["MarketName"],
                "ordertype": row["OrderType"],
                "exchange": exchange,
                "fillorder": fillorder
                },
            "time": row["Received"],
            "fields": {
                "rate": float(row["Rate"]),
                "type": row["Type"],
                "quantity": float(row["Quantity"]),
                "nounce": nounce,
                "created": row["TimeStamp"]
                }
            })


    def bulkAddMarketSummary(self, exchange, row ):
        self.bulkAdd({
            "measurement": "market_summary",
            "tags": {
                "marketname": row["MarketName"],
                "exchange": exchange
                },
            "time": row["TimeStamp"],
            "fields": {
                "ask": float(row["Ask"]),
                "basevolume": float(row["BaseVolume"]),
                "bid": float(row["Bid"]),
                "high": float(row["High"]),
                "last": float(row["Last"]),
                "low": float(row["Low"]),
                "openbuyorders": row["OpenBuyOrders"],
                "opensellorders": row["OpenSellOrders"],
                "prevday": float(row["PrevDay"]),
                "volume": float(row["Volume"]),
                "created": row["Created"]
                }
            })

    def bulkAddTA(self, exchange, market, framesize, data, speed = 0 ):
        body = {
            "measurement": "market_ta",
            "tags": {
                "marketname": market,
                "exchange": exchange,
                "framesize": framesize,
                },
            "time": data["time"],
            "fields": {
                "rsi": float(data["rsi"]),
                "mfi": float(data["mfi"]),
                "cci": float(data["cci"]),
                "cmo": float(data["cmo"]),
                "mom": float(data["mom"]),
                "dx": float(data["dx"]),
                "roc": float(data["roc"]),
                "macd": float(data["macd"]),
                "macdsig": float(data["macdsig"]),
                "macdhist": float(data["macdhist"]),
                "bb_u": float(data["bb_u"]),
                "bb_m": float(data["bb_m"]),
                "bb_l": float(data["bb_l"]),
                "bb2_u": float(data["bb2_u"]),
                "bb2_m": float(data["bb2_m"]),
                "bb2_l": float(data["bb2_l"]),
                "calcspeed": float(speed),
                }
            }
        self.bulkAdd(body)
