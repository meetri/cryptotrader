var gem = require("gemini-api")
const websocketClient =  new gem.default.WebsocketClient({ key:process.env.gemeni_key, secret:process.env.gemeni_secret, sandbox: false });

var redis = require("redis");
var chan = redis.createClient({host: process.env.REDIS_HOST,port: process.env.REDIS_PORT});

websocketClient.openMarketSocket('btcusd', () => {
  websocketClient.addMarketMessageListener(data =>
	console.log(data)
  );
  websocketClient.addMarketListener(data =>
	console.log(data)
  );
});


