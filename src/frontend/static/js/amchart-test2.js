var charts = undefined

function createChartWith ( data ){

    if (false){
        //TODO: FIX THIS LATER
        console.log("chart already exists")
        console.log( data[0].datasets[0]["dataProvider"] )
        charts.dataSets[0]["dataProvider"] = data[0].datasets[0]["dataProvider"]
        charts.validateData()
        console.log( charts.dataSets[0]["dataProvider"] )

    }else {
        console.log("creating chart")
        charts = AmCharts.makeChart( "chartdiv", {
          "type": "stock",
          "theme": "black",
          "backgroundAlpha": 0,
          "backgroundColor": "#111",

          //"color": "#fff",
          "dataSets": data[0].datasets,
          "dataDateFormat": "yyyy-mm-dd",

          "panels": [ {
              "title": "Value",
			  "showCategoryAxis": false,
              "percentHeight": 60,
			  "valueAxes": [{"id":"v1","dashLength":5}],
			  "categoryAxis": {"dashLength":5},
              "backgroundColor": "#111",
              "backgroundAlpha": 0,

              "stockGraphs": data[0].stockgraphs,

              "stockLegend": {
                "valueTextRegular": undefined,
                "periodValueTextComparing": "[[value.close]]"
              }

            },
            {
              "title": "More",
              "percentHeight": 20,
			  "marginTop": 1,
			  "showCategoryAxis": true,
			  "valueAxes": [ {
				"dashLength": 5
			  } ],

			  "categoryAxis": {
				"dashLength": 5
			  },

			  "stockGraphs": [ {
				"title": "RSI", 
				"lineColor": "tomato", 
				"lineThickness": 1, 
                "type": "line",
				"valueField": "rsi",
				"showBalloon": false,
				"fillAlphas": 0,
				"useDataSetColors": false, 
			  } ],

			  "stockLegend": {
				"markerType": "none",
				"markerSize": 0,
				"labelText": "",
				"periodValueTextRegular": "[[value.close]]"
			  }
            },

            {
			  "title": "Volume",
			  "percentHeight": 20,
			  "marginTop": 1,
			  "showCategoryAxis": true,
			  "valueAxes": [ {
				"dashLength": 5
			  } ],

			  "categoryAxis": {
				"dashLength": 5
			  },

			  "stockGraphs": [ {
				"valueField": "volume",
				"type": "column",
				"showBalloon": false,
				"fillAlphas": 1
			  } ],

			  "stockLegend": {
				"markerType": "none",
				"markerSize": 0,
				"labelText": "",
				"periodValueTextRegular": "[[value.close]]"
			  }

            }
          ],

          "chartScrollbarSettings": {
            "graph": "g1",
            "usePeriod": "10mm",
            "position": "top"
          },

          "chartCursorSettings": {
            "pan": true,
            "valueLineEnabled": true,
            "valueLineBalloonEnabled": true
          },

          "periodSelector": {
            "position": "top",
            "dateFormat": "YYYY-MM-DD JJ:NN",
            "inputFieldWidth": 150,
                "periods": [ {
              "period": "hh",
              "count": 1,
              "label": "1 hour"
            }, {
              "period": "hh",
              "count": 2,
              "label": "2 hours"
            }, {
              "period": "hh",
              "count": 5,
              "selected": true,
              "label": "5 hour"
            }, {
              "period": "hh",
              "count": 12,
              "label": "12 hours"
            }, {
              "period": "MAX",
              "label": "MAX"
            } ]
          },

          "panelsSettings": {
            //    "color": "#fff",
            "plotAreaFillColors": "#111",
            "plotAreaFillAlphas": 1,
            "marginLeft": 60,
            "marginTop": 5,
            "marginBottom": 5
          },

          "categoryAxesSettings": {
            "minPeriod": "mm",
            "equalSpacing": true,
            //"gridColor": "#333",
            //"gridAlpha": 1
          },

          "valueAxesSettings": {
            "gridColor": "#111",
            "gridAlpha": 1,
            "inside": false,
            "showLastLabel": true
          },

          "legendSettings": {
            "position": "top",
            "valueWidth": 150
            //"color": "#fff"
          },

          "stockEventsSettings": {
            "showAt": "high",
            "type": "pin"
          },

          "balloon": {
            "textAlign": "left",
            "offsetY": 10
          },

        } );
    }


}

