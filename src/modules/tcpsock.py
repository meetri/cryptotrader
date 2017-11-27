import socket
from threading import Thread

class TcpSock(object):

    def __init__(self,host="127.0.0.1",port=9999, responder = None ):
        self.host = host
        self.port = port
        self.bufsize = 128
        self.sock = None
        self.socketThread = None
        self.responder = responder


    def _connect(self):
        while True:
            conn, addr = self.sock.accept()
            while True:
                data = conn.recv(self.bufsize)
                if not data: break
                data = data.decode()
                if self.responder == None:
                    conn.send(data)
                else:
                    msg = "{}\n".format(self.responder.dataProvider().getInfo(data))
                    conn.send( msg.encode() )

            conn.close()

    def get(self,msg="nothing"):

        sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        r = sock.connect((self.host,self.port))
        ret = sock.send( msg.encode() )

        chunks = []
        done = False
        while not done:
            chunk = sock.recv(2048).decode()
            chunks.append(chunk)
            done = chunk[-1] == "\n"

        msg = "".join(chunks)
        sock.close()

        return msg


    def start(self):
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.sock.bind((self.host,self.port))
        self.sock.listen(1)

        self.socketThread = Thread(target = self._connect )
        self.socketThread.start()
