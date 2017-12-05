var charts = undefined

function createChartWith ( data ){

    if (false){// charts != undefined){
        //TODO: FIX THIS LATER
        console.log("chart already exists")
		var newChartData = []
		var newdata = data[0].datasets[0]["dataProvider"]
		for (idx in newdata){
			newChartData.push(newdata[idx])
		}
		console.log(charts.dataSets[0]["dataProvider"])
		charts.dataSets[0]["dataProvider"] = newChartData
		charts.validateData()
		charts.validateNow()

    }else {

        for (idx in data[0].datasets[0]["stockEvents"]){
            data[0].datasets[0]["stockEvents"][idx]["date"] = new Date(data[0].datasets[0]["stockEvents"][idx]["date"])
        }


        charts = AmCharts.makeChart( "chartdiv", {
          "type": "stock",
          "theme": "black",

          "dataSets": data[0].datasets,
          "panels": [ {
              "title": "Value",
			  "showCategoryAxis": false,
              "creditsPosition" : "bottom-right",
              "drawingIconsEnabled": false,
              "percentHeight": 55,
			  "valueAxes": [{"id":"v1","dashLength":5}],
			  "categoryAxis": {"dashLength":5},
              "stockGraphs": data[0].stockgraphs[0],
              "stockLegend": {
                "valueTextRegular": undefined,
                "periodValueTextComparing": "[[value.close]]"
              }
            },
            {
              "title": "More",
              "percentHeight": 15,
              "creditsPosition" : "bottom-right",
			  "marginTop": 1,
			  "showCategoryAxis": true,
              "valueAxes": [{
                  "id":"v1",
                  "maximum": 100,
                  "minimum": 0,
                  "position": "left",
                  "guides": [ {
                     "value": 80,
                     "lineAlpha": 0.8,
                     "lineColor": "#c00",
                     "label": "oversold",
                     "position": "right"
                   },{
                     "value": 20,
                     "lineAlpha": 0.8,
                     "lineColor": "limegreen",
                     "label": "overbought",
                     "position": "right"
                   }],
              },{
                  "id":"v2",
                  "position": "right"
              }],
              "stockGraphs": data[0].stockgraphs[1],
			  "stockLegend": {
				"markerType": "none",
				"markerSize": 0,
				"labelText": "",
				"periodValueTextRegular": "[[value.rsi]]"
			  }
            },

            {
              "title": "More2",
              "percentHeight": 20,
              "creditsPosition" : "bottom-right",
			  "marginTop": 1,
			  "showCategoryAxis": true,
              "valueAxes": [{
                  "id":"v1",
                  "position": "left"
              }, {
                  "id":"v2",
                  "position": "right"
              }],
              "stockGraphs": data[0].stockgraphs[2],
			  "stockLegend": {
				"markerType": "none",
				"markerSize": 0,
				"labelText": "",
				"periodValueTextRegular": "[[value.macd]]"
			  }
            },
            {
			  "title": "Volume",
			  "percentHeight": 10,
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
				"periodValueTextRegular": "[[value.volume]]"
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
            "valueLineBalloonEnabled": false 
          },

          "periodSelector": {
            "position": "top",
            "dateFormat": "YYYY-MM-DD JJ:NN",
            "inputFieldWidth": 150,
                "periods": [ {
              "period": "hh",
              "count": 1,
              "selected": true,
              "label": "1 hour"
            }, {
              "period": "hh",
              "count": 2,
              "label": "2 hours"
            }, {
              "period": "hh",
              "count": 5,
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
            "position": "bottom",
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

