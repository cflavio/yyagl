from socket import socket, AF_INET, SOCK_DGRAM, SOCK_STREAM, gaierror, error, \
    SOL_SOCKET, SO_REUSEADDR
from json import load
from struct import Struct
from threading import Thread, Lock
from select import select
from simpleubjson import encode, decode
from urllib2 import urlopen
from .network import AbsNetwork


class ServerThread(Thread):

    def __init__(self, eng, rpc_cb):
        Thread.__init__(self)
        self.daemon = True
        self.is_running = True
        self.lock = Lock()
        self.eng = eng
        self.rpc_cb = rpc_cb
        self.tcp_sock = socket(AF_INET, SOCK_STREAM)
        self.tcp_sock.setblocking(0)
        self.tcp_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.tcp_sock.bind(('', 9099))
        self.tcp_sock.listen(1)
        self.connections = [self.tcp_sock]
        self.conn2msgs = {}
        self.size_struct = Struct('!I')

    def run(self):
        while self.is_running:
            try:
                readable, writable, exceptional = select(
                    self.connections, self.connections, self.connections, 1)
                for s in readable:
                    if s is self.tcp_sock:
                        conn, addr = s.accept()
                        self.connections += [conn]
                        self.conn2msgs[conn] = []
                    else:
                        data = self.recv_one_message(s)
                        if data:
                            d = dict(decode(data))
                            if 'is_rpc' in d:
                                self.eng.cb_mux.add_cb(self.rpc_cb, [d, s])
                            else:
                                self.eng.cb_mux.add_cb(self.read_cb, [d['payload'], s])
                for s in writable:
                    with self.lock:
                        if self.conn2msgs[s]:
                            msg = self.conn2msgs[s].pop(0)
                            s.sendall(self.size_struct.pack(len(msg)))
                            s.sendall(msg)
                for s in exceptional: print 'exception', s.getpeername()
            except error as e: print e

    def recv_one_message(self, sock):
        lengthbuf = self.recvall(sock, self.size_struct.size)
        length = self.size_struct.unpack(lengthbuf)[0]
        return self.recvall(sock, length)

    def recvall(self, sock, count):
        buf = b''
        while count:
            newbuf = sock.recv(count)
            if not newbuf: return None
            buf += newbuf
            count -= len(newbuf)
        return buf

    def send_msg(self, conn, msg):
        with self.lock: self.conn2msgs[conn] += [msg]

    def destroy(self):
        self.is_running = False
        self.tcp_sock.close()


class Server(AbsNetwork):

    def __init__(self):
        AbsNetwork.__init__(self)
        self.tcp_sock = self.udp_sock = self.conn_cb = self.public_addr = \
        self.local_addr = self.server_thread = None
        self._functions = {}

    @property
    def connections(self): return self.server_thread.connections[1:]

    def register_cb(self, callback):
        self.read_cb = callback
        self.server_thread.read_cb = callback

    def start(self, read_cb, conn_cb):
        AbsNetwork.start(self, read_cb)
        self.conn_cb = conn_cb
        sock = socket(AF_INET, SOCK_DGRAM)
        sock.connect(('ya2.it', 8080))
        self.local_addr = sock.getsockname()[0]
        self.public_addr = load(urlopen('http://httpbin.org/ip', timeout=3))['origin']
        self.udp_sock = socket(AF_INET, SOCK_DGRAM)
        self.udp_sock.bind(('', 9099))
        self.udp_sock.setblocking(0)
        self.server_thread = ServerThread(self.eng, self.rpc_cb)
        self.server_thread.start()
        self.server_thread.read_cb = read_cb
        self.read_cb = read_cb
        self.eng.log('the server is up %s %s' % (self.public_addr, self.local_addr))

    def _actual_send(self, datagram, receiver=None):
        receivers = [cln for cln in [conn for conn in self.connections] if cln == receiver]
        dests = receivers if receiver else [conn for conn in self.connections]
        map(lambda cln: self.server_thread.send_msg(cln, datagram), dests)

    def rpc_cb(self, d, conn):
        funcname, args, kwargs = d['payload']
        if not kwargs: kwargs = {}
        kwargs['sender'] = conn
        r = self._functions[funcname](*args, **kwargs)
        self.server_thread.send_msg(conn, encode({'is_rpc': True, 'result': r}))

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

    def stop(self):
        if self.server_thread:
            self.udp_sock.close()
            self.server_thread.destroy()
            self.tcp_socket = self.conn_cb = self.server_thread = None
        else: self.eng.log('the server was already stopped')
        AbsNetwork.stop(self)
        self.eng.log('the server has been stopped')

    def destroy(self):
        AbsNetwork.destroy(self)
        self.eng.log('the server has been destroyed')
