angular.module('app', ['components'])


.config ( function($locationProvider){
    $locationProvider.html5Mode({
        enabled: true,
        requireBase: false
    });
})

.controller('botController', function($scope,$http,$timeout,$location) {

    $scope.tradeFields = ["id","time","status","limit","qty","change"];

	( function getBotInfo() {

		$http({
              method: 'GET',
              url: '/_botinfo',
              params: { bot: $location.search().bot }
        }).then( function successCallback(response){
			$scope.bot  = response.data.bot;
			$scope.indicators = response.data.indicators;
			$timeout(getBotInfo,1000)
		}, function errorCallback(response){
			console.log("failed response from server")
			$timeout(getBotInfo,5000)
		});


	})();

	( function getBotTrades() {

		$http({
              method: 'GET',
              url: '/_bottrades',
              params: { bot: $location.search().bot }
        }).then( function successCallback(response){
			$scope.trades = response.data.trades
			$timeout(getBotTrades,30000)
		}, function errorCallback(response){
			console.log("failed response from server")
			$timeout(getBotTrades,60000)
		});

	})();
    
    

});
 
