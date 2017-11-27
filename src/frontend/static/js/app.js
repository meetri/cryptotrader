angular.module('cryptoai', ['nvd3','components'])


.config ( function($locationProvider){
    $locationProvider.html5Mode({
        enabled: true,
        requireBase: false
    });

})

.directive('animateOnChange', function($timeout) {
  return function(scope, element, attr) {
    scope.$watch(attr.animateOnChange, function(nv,ov) {
      if (nv!=ov) {
		if ( parseFloat(nv) > parseFloat(ov) ){
			element.addClass('goneup');
			element.removeClass('isdown');
			element.removeClass('isup');
			$timeout(function() {
			  element.removeClass('goneup');
			  element.addClass('isup');
			}, 800); // Could be enhanced to take duration as a parameter
		}else {
            if ( parseFloat(nv).toString() == nv ){
				element.addClass('gonedown');
				element.removeClass('isdown');
				element.removeClass('isup');
				$timeout(function() {
				  element.removeClass('gonedown');
				  element.addClass('isdown');
				}, 800); // Could be enhanced to take duration as a parameter
			}else {
				if ( nv == "" ){
					element.removeClass("changed")
					element.removeClass("overbought")
					element.removeClass("oversold")
				}else if ( nv == "overbought" ){
					element.removeClass("changed")
					element.addClass("overbought")
					element.removeClass("oversold")
				}else if ( nv == "oversold"){
					element.removeClass("changed")
					element.removeClass("overbought")
					element.addClass("oversold")
				}else {
					element.addClass('changed');
					$timeout(function() {
					  element.removeClass('changed');
					}, 800); // Could be enhanced to take duration as a parameter
				}
			}
		}
      }
    });
  };
})

.controller('tacharts', function($scope,$http,$timeout,$location){

	$scope.options = {
		chart: {
			type: 'multiChart',
      showLegend: true,
			height: 450,
			margin : {
				top: 30,
				right: 60,
				bottom: 50,
				left: 70
			},
			color: d3.scale.category10().range(),
			//useInteractiveGuideline: true,
			transitionDuration: 500,
			xAxis: {
				axisLabel: 'Dates',
				tickFormat: function(d) {
					return d3.time.format('%x')(new Date( d * 1000 ));
				},
				showMaxMin: true
			},
			yAxis1: {
				axisLabel: 'Stock Price',
				tickFormat: function(d){
					return '$' + d3.format(',.8f')(d);
				},
				showMaxMin: false
			},
      yDomain2: [0,300],
			yAxis2: {
				tickFormat: function(d){
					return d3.format(',.1f')(d);
				}
			}
		}
	};

	$scope.options2 = {
		chart: {
			type: 'multiChart',
      showLegend: true,
			height: 200,
			margin : {
				top: 30,
				right: 60,
				bottom: 50,
				left: 70
			},
			color: d3.scale.category10().range(),
			//useInteractiveGuideline: true,
			transitionDuration: 500,
			xAxis: {
				axisLabel: 'Dates',
				tickFormat: function(d) {
					return d3.time.format('%x')(new Date( d * 1000 ));
				},
				showMaxMin: true
			},
			yAxis1: {
				axisLabel: 'Axis1',
				showMaxMin: true
			},
      yDomain2: [0,100],
			yAxis2: {
				axisLabel: 'Axis2',
				showMaxMin: true
			}
		}
	};

	$scope.options3 = {
		chart: {
			type: 'multiChart',
      showLegend: true,
			height: 200,
			margin : {
				top: 30,
				right: 60,
				bottom: 50,
				left: 70
			},
			color: d3.scale.category10().range(),
			//useInteractiveGuideline: true,
			transitionDuration: 500,
			xAxis: {
				axisLabel: 'Dates',
				tickFormat: function(d) {
					return d3.time.format('%x')(new Date( d * 1000 ));
				},
				showMaxMin: true
			},
			yAxis1: {
				axisLabel: 'Axis1',
				showMaxMin: true
			},
			yAxis2: {
				axisLabel: 'Axis2',
				showMaxMin: true
			}
		}
	};

	//$scope.data = generateData();

	(function getChartdata(){
		
		$http({
              method: 'GET',
              url: '/_tacharts',
              params: { bot: $location.search().bot }

        }).then( function successCallback(response){
			
            $scope.data = response.data["primary"]
            $scope.data2 = response.data["secondary"] 
            $scope.data3 = response.data["tertiary"] 

			$timeout(getChartdata,2000)
		}, function errorCallback(response){
			console.log("failed response from server")
			$timeout(getChartdata,30000)
			//$timeout(getBotChart,30000)

		});

	})();


})

.controller('candlestickBarChartCtrl', function($scope,$http,$timeout,$location){

	$scope.config = {
		visible: true,
		extended: false,
		refreshDataOnly: true,
		deepWatchOptions: false,
		deepWatchData: true,
		deepWatchDataDepth: 2,
		debounce: 10
	}

	$scope.options = {
		chart: {
			type: 'candlestickBarChart',
			height: 450,
			margin : {
				top: 20,
				right: 20,
				bottom: 40,
				left: 60
			},
			x: function(d){ return d['date']; },
			y: function(d){ return d['close']; },
			duration: 100,
			showLegend: true,
            interactive: false,
            useInteractiveGuideline: false,
            tooltip: {
                contentGenerator: function(e){
                    console.log(e)
                    return "<span>Hello World</span>"
                }
            },
			xAxis: {
				axisLabel: 'Dates',
				tickFormat: function(d) {
					return d3.time.format('%x')(new Date( d * 1000 ));
				},
				showMaxMin: true
			},

			yAxis: {
				axisLabel: 'Stock Price',
				tickFormat: function(d){
					return '$' + d3.format(',.8f')(d);
				},
				showMaxMin: false
			},
			zoom: {
				enabled: true,
				scaleExtent: [1, 10],
				useFixedDomain: false,
				useNiceScale: true,
				horizontalOff: false,
				verticalOff: true,
				unzoomEventType: 'dblclick.zoom'
			}
		}
	};

	( function getBotChart() {

		$http({
              method: 'GET',
              url: '/_botchart',
              params: { bot: $location.search().bot }
        }).then( function successCallback(response){
			$scope.data = response.data
			$timeout(getBotChart,10000)
		}, function errorCallback(response){
			console.log("failed response from server")
			$timeout(getBotChart,30000)
		});


	})();

	$scope.data = [];

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
			$timeout(getBotTrades,5000)
		}, function errorCallback(response){
			console.log("failed response from server")
			$timeout(getBotTrades,60000)
		});

	})();
    
    

});
 
