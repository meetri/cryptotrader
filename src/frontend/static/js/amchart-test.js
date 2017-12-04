var chart = AmCharts.makeChart( "chartdiv", {
  "type": "stock",
  "theme": "black",
  "backgroundAlpha": 0,
  "backgroundColor": "#111",

  //"color": "#fff",
  "dataSets": [ {
    "title": "MSFT",
    "fieldMappings": [ {
      "fromField": "open",
      "toField": "open"
    }, {
      "fromField": "high",
      "toField": "high"
    }, {
      "fromField": "low",
      "toField": "low"
    }, {
      "fromField": "close",
      "toField": "close"
    }, {
      "fromField": "volume",
      "toField": "volume"
    }, {
      "fromField": "sma",
      "toField": "sma"
    }, {
      "fromField": "ema",
      "toField": "ema"
    } ],
    "compared": false,
    "categoryField": "date",

    /**
     * data loader for data set data
     */
    "dataLoader": {
      "url": "/_amcharts?bot=58052",
      "format": "json",
      "showCurtain": true,
      "showErrors": true,
      "async": true,
      "postProcess": function(data,options){
          return data[0]["values"]
      }
    },

  }],



  "dataDateFormat": "YYYY-MM-DD",

  "panels": [ {
      "title": "Value",
      "percentHeight": 70,
	  "backgroundColor": "#111",
	  "backgroundAlpha": 0,

      "stockGraphs": [ {
        "type": "candlestick",
        "id": "g1",
        "openField": "open",
        "closeField": "close",
        "highField": "high",
        "lowField": "low",
        "valueField": "close",
        "lineColor": "#fff",
        "fillColors": "#fff",
        "negativeLineColor": "#db4c3c",
        "negativeFillColors": "#db4c3c",
        "fillAlphas": 1,
        "comparedGraphLineThickness": 2,
        "columnWidth": 0.7,
        "useDataSetColors": false,
        "comparable": true,
        "compareField": "close",
        "showBalloon": false,
        "proCandlesticks": true
      },{
        "id": "g2",
        "lineColor": "#FF0000",
        "lineThickness": 2,
        "valueField": "sma",
        "useDataSetColors": false
      },{
        "id": "g3",
        "lineColor": "#0000FF",
        "lineThickness": 2,
        "valueField": "ema",
        "useDataSetColors": false
      }],

      "stockLegend": {
        "valueTextRegular": undefined,
        "periodValueTextComparing": "[[value.close]]%"
      }

    },

    {
      "title": "Volume",
      "percentHeight": 30,
      "marginTop": 1,
      "columnWidth": 0.6,
      "showCategoryAxis": false,

      "stockGraphs": [ {
        "valueField": "volume",
        "type": "column",
        "fillAlphas": 1,
        "lineColor": "#fff",
        "fillColors": "#fff",
        "negativeLineColor": "#db4c3c",
        "negativeFillColors": "#db4c3c",
        "useDataSetColors": false
      } ],

      "stockLegend": {
        "markerType": "none",
				"valueTextRegular" : " ",
      },

      "valueAxes": [ {
        "usePrefixes": true
      } ]
    }
  ],

  "panelsSettings": {
    //    "color": "#fff",
    "plotAreaFillColors": "#333",
    "plotAreaFillAlphas": 1,
    "marginLeft": 60,
    "marginTop": 5,
    "marginBottom": 5
  },

  "chartScrollbarSettings": {
    "graph": "g1",
    "usePeriod": "10mm",
    "position": "top"
  },

  "categoryAxesSettings": {
    "minPeriod": "mm",
    "equalSpacing": true,
    "gridColor": "#555",
    "gridAlpha": 1
  },

  "valueAxesSettings": {
    "gridColor": "#555",
    "gridAlpha": 1,
    "inside": false,
    "showLastLabel": true
  },

  "chartCursorSettings": {
    "pan": true,
    "valueLineEnabled": true,
    "valueLineBalloonEnabled": true
  },

  "legendSettings": {
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
  }
} );
