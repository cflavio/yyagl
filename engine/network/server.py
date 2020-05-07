from socket import error
from queue import Queue
from yyagl.engine.network.network import AbsNetwork, NetworkThread, \
    msg_rpc_answ
from yyagl.engine.network.binary import BinaryData
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

    def _rpc_cb(self, funcname, args, kwargs, sock):
        self.eng.cb_mux.add_cb(self.rpc_cb, [funcname, args, kwargs, sock])

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
        #TODO: parameters differ from overridden start
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
        receivers = [cln for cln in self.connections if cln == receiver]
        dests = receivers if receiver else self.connections
        dgram = BinaryData.pack(data_lst)
        list(map(lambda cln: self.netw_thr.send_msg(cln, dgram), dests))

    def rpc_cb(self, funcname, args, kwargs, conn):
        kwargs = kwargs or {}
        kwargs['sender'] = conn
        ret = self.fname2ref[funcname](*args, **kwargs)
        msg_size, msg_data = BinaryData.pack([msg_rpc_answ, ret])
        self.netw_thr.send_msg(conn, (msg_size, msg_data))

    def register_rpc(self, func): self.fname2ref[func.__name__] = func

    def unregister_rpc(self, func): del self.fname2ref[func.__name__]

    def on_udp_pck(self, dgram, conn):
        sender = BinaryData.unpack(dgram)[0]
        if sender not in self.addr2conn: self.addr2conn[sender] = conn

    def process_udp(self):
        try: dgram, conn = self.udp_sock.recvfrom(8192)
        except error: return
        try:
            dgram = BinaryData.unpack(dgram)
            sender, payload = dgram[0], dgram[1:]
            self.read_cb(payload, sender)
        except IndexError as exc: print(exc)

    def send_udp(self, data_lst, receiver):
        if receiver[0] not in self.addr2conn: return
        msg_size, msg_data = BinaryData.pack(['server'] + data_lst)
        self.udp_sock.sendto(msg_data, self.addr2conn[receiver[0]])
