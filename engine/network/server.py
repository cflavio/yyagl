from socket import socket, AF_INET, SOCK_DGRAM, SOCK_STREAM, gaierror, error, \
    SOL_SOCKET, SO_REUSEADDR
from json import load
from struct import Struct, error as unpack_error
from threading import Thread, Lock
from select import select
from simpleubjson import encode, decode
from urllib2 import urlopen
from .network import AbsNetwork, ConnectionError, NetworkThread


class ServerThread(NetworkThread):

    def __init__(self, eng, rpc_cb):
        NetworkThread.__init__(self, eng)
        self.rpc_cb = rpc_cb
        self.lock = Lock()
        self.conn2msgs = {}

    def _configure_socket(self):
        self.tcp_sock.setblocking(0)
        self.tcp_sock.bind(('', 9099))
        self.tcp_sock.listen(1)

    def _process_read(self, s):
        if s is self.tcp_sock:
            conn, addr = s.accept()
            conn.setblocking(1)  # required on osx
            self.connections += [conn]
            self.conn2msgs[conn] = []
        else:
            try:
                data = self.recv_one_message(s)
                if data:
                    d = dict(decode(data))
                    if 'is_rpc' in d:
                        self.eng.cb_mux.add_cb(self.rpc_cb, [d, s])
                    else:
                        self.eng.cb_mux.add_cb(self.read_cb, [d['payload'], s])
            except ConnectionError as e:
                print e
                self.connections.remove(s)

    def _process_write(self, s):
        with self.lock:
            if self.conn2msgs[s]:
                msg = self.conn2msgs[s].pop(0)
                s.sendall(self.size_struct.pack(len(msg)))
                s.sendall(msg)

    def send_msg(self, conn, msg):
        with self.lock: self.conn2msgs[conn] += [msg]


class Server(AbsNetwork):

    def __init__(self):
        AbsNetwork.__init__(self)
        self.tcp_sock = self.udp_sock = self.conn_cb = self.public_addr = \
        self.local_addr = self.network_thr = None
        self._functions = {}

    @property
    def connections(self): return self.network_thr.connections[1:]

    def start(self, read_cb, conn_cb):
        AbsNetwork.start(self, read_cb)
        self.conn_cb = conn_cb

    def _build_network_thread(self):
        return ServerThread(self.eng, self.rpc_cb)

    def _configure_udp(self): self.udp_sock.bind(('', 9099))

    def _actual_send(self, datagram, receiver=None):
        receivers = [cln for cln in [conn for conn in self.connections] if cln == receiver]
        dests = receivers if receiver else [conn for conn in self.connections]
        map(lambda cln: self.network_thr.send_msg(cln, datagram), dests)

    def rpc_cb(self, d, conn):
        funcname, args, kwargs = d['payload']
        if not kwargs: kwargs = {}
        kwargs['sender'] = conn
        r = self._functions[funcname](*args, **kwargs)
        self.network_thr.send_msg(conn, encode({'is_rpc': True, 'result': r}))

    def register_rpc(self, func): self._functions[func.__name__] = func

    def unregister_rpc(self, func): del self._functions[func.__name__]

    def process_udp(self):
        try: payload, addr = self.udp_sock.recvfrom(8192)
        except error: return
        payload = self._fix_payload(dict(decode(payload)))
        sender = payload['sender']
        if sender not in self.addr2conn:
            self.addr2conn[sender] = addr
        self.read_cb(payload['payload'], addr)

    def send_udp(self, data_lst, receiver):
        if receiver[0] not in self.addr2conn: return
        my_addr = self.my_addr if hasattr(self, 'my_addr') else 'server'
        payload = {'sender': my_addr, 'payload': data_lst}
        self.udp_sock.sendto(encode(payload), self.addr2conn[receiver[0]])
