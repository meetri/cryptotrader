import yaml

class Tools(object):

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
            return None

