require('console-stamp')(console, '[HH:MM:ss.l]');

var bittrex = require('node.bittrex.api');
var redis = require("redis");
// const { Client } = require('pg')
// const client = new Client()

var debugmode = process.env.DEBUGMODE || "true"
var get_balance = process.env.POLL_BALANCE || "false"
var queuename = process.env.QUEUE || "marketqueue"
var get_balance_interval = process.env.BALANCE_INTERVAL || 60000
var get_market_poll_interval = process.env.MARKET_POLL_INTERVAL || 10000
var get_market_summary = process.env.GET_MARKET_SUMMARY || "false"
var get_market_orders = process.env.GET_MARKET_ORDERS || "false"
var poll_market_summary = process.env.POLL_MARKET_SUMMARY || "false"
var force_exit = process.env.FORCE_EXIT || 30
var market_list = process.env.MARKET_LIST || ""

var socket_count = 0
var socket2_count = 0

var chan = redis.createClient({host: process.env.REDIS_HOST,port: process.env.REDIS_PORT});

bittrex.options({
    'apikey' : process.env.bittrex_key,
    'apisecret' : process.env.bittrex_secret
})

function create_ws_marketorders( marketlist ){
    console.log("subscribing to "+marketlist.length +" markets from marketlist")
    const websocketsclient = bittrex.websockets.subscribe(marketlist, function(data) {
        blob = JSON.stringify(data)
        chan.rpush(queuename, blob);
        socket_count++;
        if ( debugmode == "true" && (socket_count % 100 == 0) ){
            console.log("marketlist websocket event count",socket_count)
        }
    });
}

function create_ws_marketsummary(){
    console.log("subscribing marketsummary feed")
    var websocketsclient2 = bittrex.websockets.listen( function(data) {
        chan.rpush(queuename, JSON.stringify(data));
        socket2_count++;
        if ( debugmode == "true" && (socket2_count % 5 == 0) ){
            console.log("summary websocket event count",socket2_count)
        }
    });
}


function getBalances(){
    bittrex.getbalances(function( data ) {
        if ( data){
            console.log("getting balance")
            blob = { "M":"account", "A": data }
            chan.rpush(queuename, JSON.stringify(blob));
        }else {
            console.log("error getting balance")
        }
    });
}

function getMarketSummaries() {
	console.log("get market summaries")
	bittrex.getmarketsummaries( function( data, err ) {
		if ( err ){
			console.error("problem getting market summaries",err)
		}else {

			if ( data !== true && data.length > 3 ){
				blob = { "M":"updateSummaryState", "A": [{"Deltas": data}] }
				chan.rpush(queuename, JSON.stringify(blob));
			}
		}
	});
}

function getOutOfHere(){
    console.log("getting outa heya")
    process.exit(1)
}

if ( force_exit > 0 ) {
    force_exit_interval = force_exit * 1000 * 60
    console.log("setting exit timeout to " + force_exit_interval + " milliseconds " )
    setTimeout( getOutOfHere, force_exit_interval )
}

if ( get_balance == "true" ){
    setInterval( getBalances, get_balance_interval )
}

if ( poll_market_summary == "true") {
    setInterval( getMarketSummaries, get_market_poll_interval )
}

marketlist = []
if (get_market_orders == "true"){

    if ( market_list.length == 0 ){
        client.connect()
        client.query("SELECT market_name FROM markets.marketlist WHERE enabled=true", (err, res) => {
            if ( err ){
                console.log("there was an error",err)
            }else if ( res ){
                for ( var i in res["rows"] ){
                    mn = res['rows'][i].market_name;
                    marketlist.push(mn);
                }
                console.log(marketlist)
                create_ws_marketorders(marketlist)
            }
        })
    }else {
        console.log("scraping the following markets: " + market_list)
        create_ws_marketorders(market_list.split(" "))
    }

}

if ( get_market_summary == "true" ){
    create_ws_marketsummary()
}

