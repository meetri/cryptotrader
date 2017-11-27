import os
import psycopg2
import psycopg2.pool
import psycopg2.extras

class PgPool(object):

    _instance = None

    def __init__(self,minpoolsize=1,maxpoolsize=2, connInfo = None):

        if connInfo is None:
            connInfo = {
                    "database":  os.getenv("PGDATABASE","crypto"),
                    "user": os.getenv("PGUSER","postgres"),
                    "host": os.getenv("PGHOST","localhost"),
                    "port": os.getenv("PGPORT","5432"),
                    "password": os.getenv("PGPASSWORD","helloworld")
                    }

        try:
            self.db  = psycopg2.pool.ThreadedConnectionPool(minpoolsize,maxpoolsize,**connInfo)
        except Exception as ex:
            print ("Error: {}".format(ex))

    @staticmethod
    def setup(minpoolsize,maxpoolsize,connInfo):
        if PgPool._instance is None:
            PgPool._instance = PgPool(minpoolsize,maxpoolsize,connInfo)
        else:
            print("WARN: pgpool already setup")

        return PgPool._instance

    @staticmethod
    def getInstance():
        if PgPool._instance is None:
            PgPool._instance = PgPool()
        return PgPool._instance


    def get_dict_cursor(self):
        conn = self.db.getconn()
        res = conn.cursor(cursor_factory= psycopg2.extras.DictCursor )
        self.db.putconn(conn)
        return res

    def get_cursor(self):
        conn = self.db.getconn()
        res = conn.cursor()
        self.db.putconn(conn)
        return res

    def insert(self,  schema, mapdata, extra = ""):
        conn = self.db.getconn()
        cur = conn.cursor()

        values =  sql = ""
        vdata = []
        for k,v in mapdata.items():
            sql += "{},".format( k )
            values += "%s,"
            vdata += [v]

        sql = "INSERT INTO {} ( {} ) VALUES ( {} ) {} RETURNING id".format(schema, sql[0:-1],values[0:-1],extra)

        try:
            cur.execute(sql,vdata)
            conn.commit()
            insert_id = cur.fetchone()[0]
            rowcount = cur.rowcount
        except Exception as ex:
            print("postgresql insert error: {}".format(ex))
            insert_id = None
        finally:
            self.db.putconn(conn)
            cur.close()

        return insert_id


    def select(self, query, params ):
        cur = self.get_dict_cursor()
        cur.execute(query,params)
        res = cur.fetchall()
        cur.close()
        return res


    def update(self,  schema, pkey, mapdata, srcdata):

        if pkey in srcdata and srcdata[pkey] is not None:

            sql = ""
            vdata = []
            for k,v in mapdata.items():
                if k != pkey and mapdata[k] != srcdata[k]:
                    sql += "{}=%s,".format( k )
                    vdata += [v]

            rowcount = 0
            if len(sql) > 0:
                conn = self.db.getconn()
                cur = conn.cursor()
                try:
                    sql = "UPDATE {} SET {} WHERE {}={}".format(schema, sql[0:-1], pkey, srcdata[pkey])
                    cur.execute(sql,vdata)
                    conn.commit()
                except Exception as ex:
                    print("problem with update {}".format(ex))
                    #raise ex
                finally:
                    self.db.putconn(conn)
                    cur.close()

                rowcount = cur.rowcount

            return rowcount

