class DoubleBand(object):

    def __init__(self,analyzer,outer,inner):
        self.analyzer = analyzer
        self.oband = outer
        self.iband = inner


    def debug(self,messages):

        messages.append("double band debug messages")

        if self.enteringLowerBand():
            messages.append("entering lower band")
        if self.exitingLowerOuterBand():
            messages.append("exiting lower outer band")
        if self.enteringLowerOuterBand():
            messages.append("entering lower outer band")
        if self.exitingLowerOuterBand():
            messages.append("exiting lower outer band")
        if self.risingAboveCenter():
            messages.append("rising above center")
        if self.enteringUpperBand():
            messages.append("entering upper band")
        if self.exitingOuterUpperBand():
            messages.append("exiting outer upper band")
        if self.enteringOuterUpperBand():
            messages.append("entering outer upper band")
        if self.exitingUpperBand():
            messages.append("exiting upper band")
        if self.settingBelowCenter():
            messages.append("setting below center")
        if self.isInLowerBand():
            messages.append("is in lower band")
        if self.isInUpperBand():
            messages.append("is in upper band")
        if self.isAboveUpperBand():
            messages.append("is above upper band")
        if self.isBelowLowerBand():
            messages.append("is below lower band")
        if self.isUpperCenter():
            messages.append("is upper center")
        if self.isLowerCenter():
            messages.append("is lower center")

        return messages


    def isInLowerBand(self):
        if ( self.analyzer.last("closed") >= self.oband.low() and
                self.analyzer.last("closed") <= self.iband.low() ):
            return True
        return False

    def isInUpperBand(self):
        if ( self.analyzer.last("closed") >= self.iband.top() and
                self.analyzer.last("closed") <= self.oband.top() ):
            return True
        return False

    def isAboveUpperBand(self):
        if self.analyzer.last("closed") >= self.oband.top():
            return True
        return False


    def isBelowLowerBand(self):
        if self.analyzer.last("closed") <= self.oband.low():
            return True
        return False

    def isUpperCenter(self):
        if ( self.analyzer.last("closed") >= self.iband.middle() and
                self.analyzer.last("closed") <= self.iband.top() ):
            return True
        return False


    def isLowerCenter(self):
        if ( self.analyzer.last("closed") <= self.iband.middle() and
                self.analyzer.last("closed") >= self.iband.top() ):
            return True
        return False


    def enteringUpperBand(self):
        if ( self.analyzer.last("closed",2) < self.iband.top(2) and
                self.analyzer.last("closed") >= self.iband.top() ):
            return True


    def exitingUpperBand(self):
        if ( self.analyzer.last("closed",2) > self.oband.top(2) and
                self.analyzer.last("closed") < self.oband.top() ):
            return True


    def exitingOuterUpperBand(self):
        if ( self.analyzer.last("closed",2) < self.oband.top(2) and
                self.analyzer.last("closed") > self.oband.top() ):
            return True


    def enteringOuterUpperBand(self):
        if ( self.analyzer.last("closed",2) > self.oband.top(2) and
                self.analyzer.last("closed") < self.oband.top() ):
            return True


    def enteringLowerBand(self):
        if ( self.analyzer.last("closed",2) > self.iband.low(2) and
                self.analyzer.last("closed") < self.iband.low() ):
            return True


    def exitingLowerBand(self):
        if ( self.analyzer.last("closed",2) > self.oband.low(2) and
                self.analyzer.last("closed") < self.oband.low() ):
            return True


    def enteringLowerOuterBand(self):
        if ( self.analyzer.last("closed",2) < self.oband.low(2) and
                self.analyzer.last("closed") > self.oband.low() ):
            return True


    def exitingLowerOuterBand(self):
        if ( self.analyzer.last("closed",2) > self.oband.low(2) and
                self.analyzer.last("closed") < self.oband.low() ):
            return True


    def risingAboveCenter(self):
        if ( self.analyzer.last("closed",2) < self.oband.middle(2) and
                self.analyzer.last("closed") > self.oband.middle() ):
            return True


    def settingBelowCenter(self):
        if ( self.analyzer.last("closed",2) > self.oband.middle(2) and
                self.analyzer.last("closed") < self.oband.middle() ):
            return True

