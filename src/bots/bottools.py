import os,sys,yaml
from columnize import Columnize

class BotTools(object):

    @staticmethod
    def draw_bot_results( stdscr, bot ):
        stdscr.clear()
        Columnize.draw_table( stdscr, 0, "name,signal,cs,last,high,low,time", [bot.get_results()] )
        lr = Columnize.cursesMultiMap(stdscr,3, bot.get_indicators())

        Columnize.draw_list( stdscr,0, 135, bot.get_debug_messages(), header="Bot Debug Messages" )

        s = []
        b = []
        for trade in bot.get_monitored_trades():
            if trade.trade_type == "sell" and trade.status not in ["cancelled"]:
                s += [trade.details()]
            elif trade.trade_type == "buy" and trade.status not in ["cancelled"]:
                b += [trade.details()]

        if len(s) > 0:
            lr = Columnize.cursesMultiMap(stdscr,lr+1, s,sameheader=True)

        if len(b) > 0:
            Columnize.cursesMultiMap(stdscr,lr+1, b,sameheader=True)

        stdscr.refresh()


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
