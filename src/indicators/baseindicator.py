import os,sys,talib,numpy,math,logging,numbers
from collections import OrderedDict

class BaseIndicator(object):

    def __init__(self,csdata,config):
        self.log = logging.getLogger('crypto')
        self.csdata = csdata
        self.label = config.get("label","")
        self.config = config
        self.analysis = None

        self.chartcolors = config.get("chartcolors",["#FFF"])
        self.chart_metric_keys = config.get("chartkeys",[self.label])
        self.chart_type = config.get("charttypes",["line"])
        self.chart_axis = config.get("chartaxis",["v1"])

        self.scalefactor = 1048576
        self.data = None
        self.chart_scale = 0


    def get_data(self):
        return self.data


    def scaledown(self,data):

        ndata = []
        for i in range(0,len(data)):
            if isinstance(data[i],numbers.Number):
                ndata.append( data[i] / self.scalefactor )
            else:
                ndata.append([])
                for j in range(0,len(data[i])):
                    ndata[i].append( data[i][j] / self.scalefactor )

        return ndata
        # return ndata


    def scaleup(self,data):
        sdata = []
        if data is not None:
            for v in data:
                if v is not None and isinstance(v,numbers.Number):
                    sdata.append( v * self.scalefactor )
                else:
                    sdata.append ( v )

        return sdata
        #return numpy.array(sdata)


    def mergeGraphConfig(self,metric,stockgraph):
        """used for amcharts"""
        stockgraph["type"] = self.get_chart_type(metric)
        stockgraph["lineColor"] = self.get_chart_metric_colors(metric)
        stockgraph["valueAxis"] = self.get_chart_axis(metric)
        return stockgraph


    def get_chart_axis(self,metric):
        try:
            idx = self.chart_metric_keys.index(metric)
            return self.chart_axis[idx]
        except:
            self.log.error("cant find chart axis for {}".format(metric))
            return "v1"


    def get_chart_type(self,metric):
        try:
            idx = self.chart_metric_keys.index(metric)
            return self.chart_type[idx]
        except:
            self.log.error("cant find chart type for {}".format(metric))
            return "line"


    def get_chart_metric_colors(self,label):
        try:
            idx = self.chart_metric_keys.index(label)
            return self.chartcolors[idx]
        except:
            self.log.error("cant find color for {}".format(label))
            return "#999"

    def get_chart_metric_keys(self):
        return self.chart_metric_keys

    def get_chart_metrics(self,index = 0, scale = 0):
        if len(self.chart_metric_keys) > 1:
            if not numpy.isnan(self.data[0][index]):
                m = {}
                for key in self.chart_metric_keys:
                    m[key] = self.data[self.chart_metric_keys.index(key)][index]
                return m
        else:
            if not numpy.isnan(self.data[index]):
                m = {}
                for key in self.chart_metric_keys:
                    m[key] = self.data[index]
                return m


    def get_chart_scale(self):
        return self.chart_scale

    def get_name(self):
        return self.label

    def get_config(self):
        return self.config

    def format_view(self):
        if self.analysis is not None:
            newres = dict(self.analysis["analysis"])
            return newres


