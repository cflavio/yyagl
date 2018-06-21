from socket import socket, AF_INET, SOCK_DGRAM, error, SOCK_STREAM, \
    SOL_SOCKET, SO_REUSEADDR
from select import select
from decimal import Decimal
from json import load
from urllib2 import urlopen
from threading import Thread
from struct import Struct, error as unpack_error
from simpleubjson import encode
from yyagl.gameobject import GameObject


class NetworkError(Exception): pass


class ConnectionError(Exception): pass


class NetworkThread(Thread):

    def __init__(self, eng):
        Thread.__init__(self)
        self.daemon = True
        self.eng = eng
        self.is_running = True
        self.size_struct = Struct('!I')
        self.tcp_sock = socket(AF_INET, SOCK_STREAM)
        self.tcp_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self._configure_socket()
        self.connections = [self.tcp_sock]

    def run(self):
        while self.is_running:
            try:
                readable, writable, exceptional = select(
                    self.connections, self.connections, self.connections, 1)
                for sock in readable: self._process_read(sock)
                for sock in writable: self._process_write(sock)
                for sock in exceptional: print 'exception', sock.getpeername()
            except error as exc: print exc

    def recv_one_message(self, sock):
        lengthbuf = self.recvall(sock, self.size_struct.size)
        try: length = self.size_struct.unpack(lengthbuf)[0]
        except unpack_error as exc:
            print exc
            raise ConnectionError()
        return self.recvall(sock, length)

    @staticmethod
    def recvall(sock, count):
        buf = b''
        while count:
            newbuf = sock.recv(count)
            if not newbuf: return None
            buf += newbuf
            count -= len(newbuf)
        return buf

    def destroy(self):
        self.is_running = False
        self.tcp_sock.close()


class AbsNetwork(GameObject):

    rate = .1

    def __init__(self):
        GameObject.__init__(self)
        self.network_thr = self.read_cb = self.udp_sock = self.conn_cb = \
            self.tcp_socket = self.udp_sock = self.public_addr = \
            self.local_addr = None
        self.addr2conn = {}

    def start(self, read_cb):
        self.eng.attach_obs(self.on_frame, 1)
        self.read_cb = read_cb
        sock = socket(AF_INET, SOCK_DGRAM)
        sock.connect(('ya2.it', 8080))
        self.local_addr = sock.getsockname()[0]
        res = urlopen('http://httpbin.org/ip', timeout=3)
        self.public_addr = load(res)['origin']
        self.udp_sock = socket(AF_INET, SOCK_DGRAM)
        self.udp_sock.setblocking(0)
        self._configure_udp()
        self.network_thr = self._build_network_thread()
        self.network_thr.start()
        self.network_thr.read_cb = read_cb
        self.read_cb = read_cb
        args = (self.__class__.__name__, self.public_addr, self.local_addr)
        self.eng.log('%s is up %s %s' % args)

    def register_cb(self, callback):
        self.read_cb = callback
        self.network_thr.read_cb = callback

    def send(self, data_lst, receiver=None):
        self._actual_send(encode({'payload': data_lst}), receiver)

    def on_frame(self): self.process_udp()

    @staticmethod
    def _fix_payload(payload):
        ret = {'sender': payload['sender']}

        def __fix(elm):
            return float(elm) if isinstance(elm, Decimal) else elm
        ret['payload'] = [__fix(payl) for payl in payload['payload']]
        return ret

    @property
    def is_active(self):
        observers = self.eng.event.observers.values()
        return self.on_frame in [obs.mth for olst in observers for obs in olst]

    def stop(self):
        if not self.network_thr:
            self.eng.log('%s was already stopped' % self.__class__.__name__)
            return
        self.udp_sock.close()
        self.network_thr.destroy()
        self.tcp_socket = self.conn_cb = self.network_thr = None
        self.eng.detach_obs(self.on_frame)
        self.udp_sock.close()
        self.addr2conn = {}
        self.udp_sock = None
        self.eng.log('%s has been stopped' % self.__class__.__name__)

    def destroy(self):
        self.stop()
        self.eng.log('%s has been destroyed' % self.__class__.__name__)
        GameObject.destroy(self)
