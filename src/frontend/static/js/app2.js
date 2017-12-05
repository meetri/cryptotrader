angular.module('cryptoai', ['components'])

.controller('botDataController', function($scope,$http,$timeout,$location){

    $scope.botFields = ["name","last","signal","time"];
    $scope.tradeFields = ["order_type","status","qty","rate","growth","time"];

	( function getBotData() {

        var chart_refresh = $location.search().refresh || 60000

		$http({
              method: 'GET',
              url: '/_botdata',
              params: { bot: $location.search().bot }
        }).then( function successCallback(response){

            createChartWith ( response.data["charts"] )

			$scope.bot  = response.data["info"].bot;
			$scope.indicators = response.data["info"].indicators;
			$scope.signals = response.data["info"].signals;
			$scope.signal_history = response.data["info"].signal_history;
			$scope.logs = response.data["info"].debug;

            $scope.trades = response.data["trades"].trades

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

			$timeout(getBotData,chart_refresh)
		}, function errorCallback(response){
			console.log("failed response from server")
			$timeout(getBotData,60000)
		});


	})();

})

 
