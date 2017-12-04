angular.module('components', [])
 
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

  .directive('tabs', function() {
    return {
      restrict: 'E',
      transclude: true,
      scope: {},
      controller: function($scope, $element) {
        var panes = $scope.panes = [];
 
        $scope.select = function(pane) {
          angular.forEach(panes, function(pane) {
            pane.selected = false;
          });
          pane.selected = true;
        }
 
        this.addPane = function(pane) {
          if (panes.length == 0) $scope.select(pane);
          panes.push(pane);
        }
      },
      template:
        '<div class="tabbable">' +
          '<ul class="nav nav-tabs">' +
            '<li ng-repeat="pane in panes" ng-class="{active:pane.selected}">'+
              '<a href="" ng-click="select(pane)">{{pane.title}}</a>' +
            '</li>' +
          '</ul>' +
          '<div class="tab-content" ng-transclude></div>' +
        '</div>',
      replace: true
    };
  })
 
  .directive('pane', function() {
    return {
      require: '^tabs',
      restrict: 'E',
      transclude: true,
      scope: { title: '@' },
      link: function(scope, element, attrs, tabsController) {
        tabsController.addPane(scope);
      },
      template:
        '<div class="tab-pane" ng-class="{active: selected}" ng-transclude>' +
        '</div>',
      replace: true
    };
  })
