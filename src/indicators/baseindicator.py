import os,sys,talib,numpy,math,logging,numbers
from collections import OrderedDict

class BaseIndicator(object):

    def __init__(self,csdata,label,config):
        self.log = logging.getLogger('crypto')
        self.csdata = csdata
        self.label = label
        self.config = config
        self.analysis = None

        self.scalefactor = 1048576
        self.data = None


    def get_data(self):
        return self.data

    def get_secondary_charts(self):
        return []

    def get_tertiary_charts(self):
        return []

    def get_charts(self):
        return []

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


    def get_name(self):
        return self.label

    def get_config(self):
        return self.config

    def format_view(self):
        if self.analysis is not None:
            newres = dict(self.analysis["analysis"])
            return newres


