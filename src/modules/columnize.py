import logging,curses
from collections import OrderedDict

class Columnize(object):

    @staticmethod
    def draw_list( stdscr, line, xofs, rows , header = ""):

        if len(header) > 0:
            try:
                stdscr.addstr( line, xofs, header)
                line += 1
            except:
                pass

        for row in rows:
            try:
                stdscr.addstr( line, xofs, str(row) )
                line += 1
            except:
                pass

        return line


    @staticmethod
    def draw_table( stdscr, line, headers, rows , margin = 4, xofs = 0, showheader = True ):
        margin = 4
        colwidth = []

        headerlist = headers.split(",")

        idx = 0
        # get column width
        for row in rows:
            for header in headerlist:
                item = row[header]
                w = len(str(item)) + margin
                if showheader:
                    w2 = len(str(header)) + margin
                    if w2 > w:
                        w = w2

                if len(colwidth) > idx:
                    if colwidth[idx] < w:
                        colwidth[idx] = w
                else:
                    colwidth += [ w ]
                idx += 1


        for row in rows:
            if showheader:
                cw = xofs
                showheader = False
                idx = 0
                for col in headerlist:
                    try:
                        stdscr.addstr( line, cw, str(col), curses.A_BOLD  )
                    except:
                        break
                    cw += colwidth[idx]
                    idx += 1
                line += 1

            cw = 0
            idx = 0
            for col in headerlist:
                item = str(row[col])
                try:
                    stdscr.addstr( line ,cw, item )
                except:
                    break
                cw += colwidth[idx]
                idx += 1
            line += 1


    @staticmethod
    def cursesMapRow( stdscr, line, row, margin = 4, xofs = 0 ):
        cw = xofs
        for col, item in row.items():
            out = "{}:{}".format(col,str(item))
            w = len(out) + margin
            try:
                stdscr.addstr( line, cw, out )
                cw += w
            except:
                pass


    @staticmethod
    def cursesMultiMap( stdscr, line, rows, showheader = True, sameheader = False):

        margin = 4
        colwidth = []

        # get column width
        for row in rows:
            for idx,col in enumerate(row):
                item = row[col]
                w = len(str(item)) + margin
                if showheader:
                    w2 = len(str(col)) + margin
                    if w2 > w:
                        w = w2

                if len(colwidth) > idx:
                    if colwidth[idx] < w:
                        colwidth[idx] = w
                else:
                    colwidth += [ w ]

        for row in rows:
            if showheader:
                cw = 0
                if sameheader:
                    showheader = False
                for idx,col in enumerate(row):
                    try:
                        stdscr.addstr( line, cw, str(col), curses.A_BOLD )
                    except Exception as ex:
                        print(ex)
                        break
                    cw += colwidth[idx]
                line += 1

            cw = 0
            for idx,col in enumerate(row):
                item = str(row[col])
                try:
                    stdscr.addstr( line ,cw, item )
                except:
                    break
                cw += colwidth[idx]
            line += 1

        return line


    @staticmethod
    def curses( stdscr, line, row):

        margin = 4
        colwidth = []
        for idx,item in enumerate(row):
            colwidth += [ len( str(item) ) + margin ]

        col = 0
        try:
            for idx,item in enumerate(row):
                stdscr.addstr( line, col, str(item) )
                col += colwidth[idx]
        except Exception as ex:
            print("Exceptino",ex)


    @staticmethod
    def cprint(list):
        margin=4
        colwidth = {}
        for row in list:
            for idx, col in enumerate(row):
                if idx not in colwidth:
                    colwidth[idx] = []
                colwidth[idx].append(len(str(col))+margin)

        maxwidth = {}
        for idx in colwidth:
            maxwidth[idx] = max(colwidth[idx])

        for row in list:
            for idx,col in enumerate(row):
                print ( str(col).ljust( maxwidth[idx] ),end='',flush=True )
            print("")
