from socket import socket, AF_INET, SOCK_DGRAM, error, SOCK_STREAM, \
    SOL_SOCKET, SO_REUSEADDR
from select import select
from queue import Queue, Empty
from bson import dumps, loads
from decimal import Decimal
from json import load
from urllib.request import urlopen
from threading import Thread
from _thread import interrupt_main
from struct import Struct, error as unpack_error
from yyagl.gameobject import GameObject


class ConnectionError(Exception): pass


class NetworkThread(Thread):

    def __init__(self, eng, port):
        Thread.__init__(self)
        self.port = port
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
                for sock in exceptional: print('exception', sock.getpeername())
            except (error, AttributeError) as exc: print(exc)
            # AttributeError happens when the server user exits from a race,
            # then destroy is being called but _process_read is still alive
            # and self.eng.cb_mux.add_cb is invoked, but self.eng in None
            except Exception as exc:
                print(exc)
                interrupt_main()

    def _process_read(self, sock):
        try:
            data = self.recv_one_msg(sock)
            if data:
                dct = dict(loads(data))
                if 'is_rpc' in dct: self._rpc_cb(dct, sock)
                else:
                    args = [dct['payload'], sock]
                    self.eng.cb_mux.add_cb(self.read_cb, args)
        except ConnectionError as exc:
            print(exc)
            self.notify('on_disconnected', sock)
            self.connections.remove(sock)

    def _process_write(self, sock):
        try:
            msg = self._queue(sock).get_nowait()
            sock.sendall(self.size_struct.pack(len(msg)))
            sock.sendall(msg)
        except Empty: pass

    def recv_one_msg(self, sock):
        lengthbuf = self.recvall(sock, self.size_struct.size)
        try: length = self.size_struct.unpack(lengthbuf)[0]
        except (unpack_error, TypeError) as exc:
            print(exc)
            raise ConnectionError()
        return self.recvall(sock, length)

    @staticmethod
    def recvall(sock, cnt):
        buf = b''
        while cnt:
            newbuf = sock.recv(cnt)
            if not newbuf: return None
            buf, cnt = buf + newbuf, cnt - len(newbuf)
        return buf

    def destroy(self):
        self.is_running = False
        self.tcp_sock.close()
        self.eng = self.tcp_sock = self.connections = None


class AbsNetwork(GameObject):

    rate = .1
    _public_addr = None
    _local_addr = None

    def __init__(self, port):
        GameObject.__init__(self)
        self.netw_thr = self.read_cb = self.udp_sock = self.tcp_sock = \
            self.udp_sock = None
        self.port = port
        self.addr2conn = {}

    def start(self, read_cb):
        self.eng.attach_obs(self.on_frame, 1)
        self.read_cb = read_cb
        self.udp_sock = socket(AF_INET, SOCK_DGRAM)
        self.udp_sock.setblocking(0)
        self._configure_udp()
        try:
            self.netw_thr = self._bld_netw_thr()
            self.netw_thr.start()
            self.netw_thr.read_cb = read_cb
            args = self.__class__.__name__, self.port
            self.eng.log('%s is up, port %s' % args)
            return True
        except ValueError:  # e.g. empty server
            self.eng.log("can't start the network")

    def register_cb(self, callback):
        self.read_cb = callback
        self.netw_thr.read_cb = callback

    def send(self, data_lst, receiver=None):
        self.netw_thr.send_msg(dumps({'payload': data_lst}), receiver)

    def on_frame(self): self.process_udp()

    @staticmethod
    def _fix_payload(payload):
        ret = {'sender': payload['sender']}

        def __fix(elm):
            return float(elm) if isinstance(elm, Decimal) else elm
        ret['payload'] = list(map(__fix, payload['payload']))
        return ret

    @property
    def is_active(self):
        observers = self.eng.event.observers.values()
        return self.on_frame in [obs.mth for olst in observers for obs in olst]

    def stop(self):
        if not self.netw_thr:
            self.eng.log('%s was already stopped' % self.__class__.__name__)
            return
        self.udp_sock.close()
        self.netw_thr.destroy()
        self.udp_sock = self.tcp_sock = self.netw_thr = None
        self.eng.detach_obs(self.on_frame)
        self.addr2conn = {}
        self.eng.log('%s has been stopped' % self.__class__.__name__)

    def process_udp(self):
        try: dgram, conn = self.udp_sock.recvfrom(8192)
        except error: return
        dgram = self._fix_payload(dict(loads(dgram)))
        self.on_udp_pck(dgram)
        self.read_cb(dgram['payload'], conn)

    def on_udp_pck(self, dgram): pass

    def destroy(self):
        self.stop()
        self.eng.log('%s has been destroyed' % self.__class__.__name__)
        GameObject.destroy(self)
