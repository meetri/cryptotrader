import yaml
import inspect
import importlib

class Tools(object):

    def getBotConfig(fn,botname):
        root = {}
        cfg = Tools.get_bot_config(fn,botname)
        if "extend" in cfg:
            root = Tools.getBotConfig(fn,cfg["extend"])

        for k in cfg:
            if isinstance(cfg[k],dict):
                if k not in root:
                    root[k] = cfg[k]
                else:
                    for kk in cfg[k]:
                        root[k][kk] = cfg[k][kk]

            else:
                root[k] = cfg[k]

        return root


    @staticmethod
    def get_bot_config(fn,config):
        with open(fn,"r") as stream:
            try:
                data = yaml.load(stream)
                if "crypto-bots" in data:
                    if config in data["crypto-bots"]:
                        return data['crypto-bots'][config]
                    else:
                        print("{} not found in {}".format(config,data))
                else:
                    print("mybots.yaml missing crypto-bots top level config")

            except Exception as ex:
                print(ex)


    @staticmethod
    def calculateGrowth(start,current):
        if start and current:
            return (( float(start) - float(current)) / float(start) ) * 100
        else:
            return 0

    def loadClass(classname,modulename = None):
        if not classname:
            return None

        if modulename is None:
            if "." in classname:
                a = classname.split(".")
                modulename = a[0]
                classname = a[1]
            else:
                modulename = classname.lower()
        try:
            module = importlib.import_module(modulename)
            for x in dir(module):
                obj = getattr(module, x)

                if x == classname and inspect.isclass(obj):
                    return obj

        except ImportError as ex:
            return None
