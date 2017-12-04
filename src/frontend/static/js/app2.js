angular.module('cryptoai', ['components'])

.controller('tacharts', function($scope,$http,$timeout,$location){

	( function getAMCharts() {

		$http({
              method: 'GET',
              url: '/_amcharts',
              params: { bot: $location.search().bot }
        }).then( function successCallback(response){

            createChartWith ( response.data )

			$timeout(getAMCharts,5000)
		}, function errorCallback(response){
			console.log("failed response from server")
			$timeout(getAMCharts,10000)
		});


	})();



})

.controller('candlestickBarChartCtrl', function($scope,$http,$timeout,$location){
})

.controller('botController', function($scope,$http,$timeout,$location) {

    $scope.botFields = ["name","last","signal","time"];
    $scope.tradeFields = ["order_type","status","qty","rate","growth","time"];

	( function getBotInfo() {

		$http({
              method: 'GET',
              url: '/_botinfo',
              params: { bot: $location.search().bot }
        }).then( function successCallback(response){
			$scope.bot  = response.data.bot;
      $scope.backtest = response.data.backtest;
			$scope.indicators = response.data.indicators;
			$scope.signals = response.data.signals;
			$scope.signal_history = response.data.signal_history;
			$scope.logs = response.data.debug;
			$timeout(getBotInfo,2000)
		}, function errorCallback(response){
			console.log("failed response from server")
			$timeout(getBotInfo,10000)
		});


	})();

	( function getBotTrades() {

		$http({
              method: 'GET',
              url: '/_bottrades',
              params: { bot: $location.search().bot }
        }).then( function successCallback(response){
			$scope.trades = response.data.trades
      
      var sumgrowth = 0
      var sumprofit = 0
      var active_count =0
      for ( var trade in $scope.trades ){
        sumgrowth +=  $scope.trades[trade]["growth"]
        sumprofit +=  $scope.trades[trade]["profit"]
        if ( $scope.trades[trade]["status"] != "completed" ){
          active_count += 1
        }
      }

      $scope.trade_summary = {
        total: $scope.trades.length,
        active_total: active_count,
        growth: sumgrowth,
        profit: sumprofit
      }

			$timeout(getBotTrades,5000)
		}, function errorCallback(response){
			console.log("failed response from server")
			$timeout(getBotTrades,60000)
		});

	})();
    
    

});
 
