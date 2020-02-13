from socket import error
from queue import Queue, Empty
from bson import dumps, loads
from yyagl.engine.network.network import AbsNetwork, ConnectionError, NetworkThread
from yyagl.gameobject import GameObject


class ServerThread(NetworkThread, GameObject):

    def __init__(self, eng, rpc_cb, port):
        NetworkThread.__init__(self, eng, port)
        GameObject.__init__(self)
        self.rpc_cb = rpc_cb
        self.conn2msgs = {}

    def _configure_socket(self):
        self.tcp_sock.setblocking(0)
        self.tcp_sock.bind(('', self.port))
        self.tcp_sock.listen(1)

    def _process_read(self, sock):
        if sock is self.tcp_sock:
            conn, addr = sock.accept()
            conn.setblocking(1)  # required on osx
            self.connections += [conn]
            self.conn2msgs[conn] = Queue()
            self.notify('on_connected', conn)
        else:
            NetworkThread._process_read(self, sock)

    def _rpc_cb(self, dct, sock):
        self.eng.cb_mux.add_cb(self.rpc_cb, [dct, sock])

    def _queue(self, sock):
        return self.conn2msgs[sock]

    def send_msg(self, conn, msg):
        self.conn2msgs[conn].put(msg)


class Server(AbsNetwork):

    def __init__(self, port):
        AbsNetwork.__init__(self, port)
        self.conn_cb = None
        self.fname2ref = {}

    @property
    def connections(self): return self.netw_thr.connections[1:]

    def start(self, read_cb, conn_cb):
        AbsNetwork.start(self, read_cb)
        self.conn_cb = conn_cb
        self.netw_thr.attach(self.on_connected)
        self.netw_thr.attach(self.on_disconnected)

    def on_connected(self, conn):
        self.notify('on_connected', conn)

    def on_disconnected(self, conn):
        self.notify('on_disconnected', conn)

    def _bld_netw_thr(self):
        return ServerThread(self.eng, self.rpc_cb, self.port)

    def _configure_udp(self): self.udp_sock.bind(('', self.port))

    def send(self, data_lst, receiver=None):
        dgram = dumps({'payload': data_lst})
        receivers = [cln for cln in self.connections if cln == receiver]
        dests = receivers if receiver else self.connections
        list(map(lambda cln: self.netw_thr.send_msg(cln, dgram), dests))

    def rpc_cb(self, dct, conn):
        funcname, args, kwargs = dct['payload']
        kwargs = kwargs or {}
        kwargs['sender'] = conn
        ret = self.fname2ref[funcname](*args, **kwargs)
        dct = {'is_rpc': True, 'result': ret}
        self.netw_thr.send_msg(conn, dumps(dct))

    def register_rpc(self, func): self.fname2ref[func.__name__] = func

    def unregister_rpc(self, func): del self.fname2ref[func.__name__]

    def on_udp_pck(self, dgram, conn):
        sender = dgram['sender']
        if sender not in self.addr2conn: self.addr2conn[sender] = conn

    def process_udp(self):
        try: dgram, conn = self.udp_sock.recvfrom(8192)
        except error: return
        try:
            dgram = self._fix_payload(dict(loads(dgram)))
            self.read_cb(dgram['payload'], dgram['sender'])
        except IndexError as e: print(e)

    def send_udp(self, data_lst, receiver):
        if receiver[0] not in self.addr2conn: return
        dgram = {'sender': 'server', 'payload': data_lst}
        self.udp_sock.sendto(dumps(dgram), self.addr2conn[receiver[0]])
