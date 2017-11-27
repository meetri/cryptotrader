class Result(object):

    def __init__(self, success, msg = "", data = {} ):
        self.success = success
        self.msg = msg
        self.data = data

    def __str__(self):
        if self.success:
            return "Success:{}:{}".format(self.msg,self.data)
        else:
            return "Error:{}:{}".format(self.msg,self.data)

    def isOk(self):
        return self.success

    @staticmethod
    def success(msg="",data={}):
        return Result(True,msg,data)

    @staticmethod
    def fail(msg="",data={}):
        return Result(False,msg,data)
