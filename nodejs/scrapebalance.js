var bittrex = require('node.bittrex.api');
var redis = require("redis");
const { Client } = require('pg')
const client = new Client()

var chan = redis.createClient({host: process.env.REDIS_HOST,port: process.env.REDIS_PORT});
var queuename = process.env.QUEUE || "marketqueue_y"

marketlist = []

function TATimer(){
    for (var i in marketlist){
        market = marketlist[i]
        console.log("sending TA for " + market )
        blob = { "M":"indicatorBot", "A": { "market": market, "framesize": "1m" } }
        chan.rpush(queuename, JSON.stringify(blob));
        blob = { "M":"indicatorBot", "A": { "market": market, "framesize": "5m" } }
        chan.rpush(queuename, JSON.stringify(blob));
    }
}

client.connect()
client.query("SELECT market_name FROM markets.marketlist WHERE enabled=true", (err, res) => {

      if ( err ){
          console.log("there was an error",err)
      }else if ( res ){
          for ( var i in res["rows"] ){
              mn = res['rows'][i].market_name;
              marketlist.push(mn);
          }

          //marketlist = ["USDT-BTC"]
          setInterval( TATimer , 10000 );
          
      }
})
