import os,sys,redis

from pgwrapper import PgPool
from influxdb import InfluxDBClient

class ExchangeDataHandler(object):

    _instance = None

    def __init__(self):
        # instantiate postgres db
        self.pgdb = None
        self.influxdb = None
        self.redisdb = None


    def getRedisDb(self):
        if self.redisdb is None:
            redis_host = os.getenv("REDIS_HOST","localhost")
            redis_port  = int(os.getenv("REDIS_PORT","6379"))
            self.redisdb = redis.StrictRedis(host=redis_host,port=redis_port)
        return self.redisdb


    def getInfluxDb(self):
        if self.influxdb == None:
            influx_host = os.getenv("INFLUXDB_HOST","localhost")
            influx_port = os.getenv("INFLUXDB_PORT","8086")
            influx_dbname = os.getenv("INFLUXDB_DBNAME","crypto")
            self.influxdb = InfluxDBClient(influx_host,influx_port,"","",influx_dbname)
        return self.influxdb


    def getPgDb(self):
        if self.pgdb == None:
            self.pgdb = PgPool.getInstance()
        return self.pgdb

    @staticmethod
    def getInstance():
        if ExchangeDataHandler._instance is None:
            ExchangeDataHandler._instance = ExchangeDataHandler()
        return ExchangeDataHandler._instance


    def getMarketList(self,page=0,limit=10):
        "provide a space delimited list of markets to scrape"

        cur = self.getPgDb().get_cursor()
        cur.execute("""SELECT market_name FROM markets.marketlist WHERE enabled=true LIMIT %s OFFSET %s""",[limit,page*limit])
        res = cur.fetchall()
        cur.close()
        marketlist = ""
        for m in res:
           marketlist += " " + m[0]

        return marketlist.strip()

    def pushMarketQueue(self, marketName ):
        data = { "exchange":"bittrex", "market": marketName }
        self.getRedisDb().rpush("linkqueue",data)

