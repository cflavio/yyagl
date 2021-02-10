from socket import socket, AF_INET, SOCK_DGRAM, error, SOCK_STREAM, \
    SOL_SOCKET, SO_REUSEADDR
from traceback import print_exc
from logging import info
from select import select
from time import sleep
from queue import Empty
from threading import Thread
from struct import Struct, error as unpack_error
from _thread import interrupt_main
from yyagl.gameobject import GameObject
from yyagl.engine.network.binary import BinaryData


msg_rpc_call, msg_rpc_answ = range(2)


class _ConnectionError(Exception): pass


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
            sleep(.001)
            try:
                readable, writable, exceptional = select(
                    self.connections, self.connections, self.connections, 1)
                for sock in readable: self._process_read(sock)
                for sock in writable: self._process_write(sock)
                for sock in exceptional: print('exception', sock.getpeername())
            except (error, AttributeError) as exc: print_exc()
            # AttributeError happens when the server user exits from a race,
            # then destroy is being called but _process_read is still alive
            # and self.eng.cb_mux.add_cb is invoked, but self.eng in None
            except Exception as exc:
                print_exc()
                interrupt_main()

    def _process_read(self, sock):
        try:
            data = self.recv_one_msg(sock)
            if data:
                try:
                    msg = BinaryData.unpack(data)
                    if msg[0] == msg_rpc_call:
                        funcname, args, kwargs = msg[1:]
                        self._rpc_cb(funcname, args, kwargs, sock)
                    elif msg[0] == msg_rpc_answ:
                        self._rpc_cb(msg[1], sock)
                    else:
                        args = [msg, sock]
                        self.eng.cb_mux.add_cb(self.read_cb, args)
                except unpack_error as exc:
                    print(exc)
                    print_exc()
        except (_ConnectionError, TypeError) as exc:
            print_exc()
            self.notify('on_disconnected', sock)
            self.connections.remove(sock)

    def _process_write(self, sock):
        try:
            msg_size, msg_data = self._queue(sock).get_nowait()
            sock.sendall(self.size_struct.pack(msg_size))
            sock.sendall(msg_data)
        except Empty: pass

    def recv_one_msg(self, sock):
        lengthbuf = self.recvall(sock, self.size_struct.size)
        try: length = self.size_struct.unpack(lengthbuf)[0]
        except unpack_error as exc:
            print(exc)
            raise _ConnectionError()
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
            info('%s is up, port %s' % args)
            return True
        except ValueError:  # e.g. empty server
            info("can't start the network")

    def register_cb(self, callback):
        self.read_cb = callback
        self.netw_thr.read_cb = callback

    def send(self, data_lst, receiver=None):
        dgram = BinaryData.pack(data_lst)
        self.netw_thr.send_msg(dgram, receiver)

    def on_frame(self): self.process_udp()

    @property
    def is_active(self):
        observers = self.eng.event.observers.values()
        return self.on_frame in [obs.mth for olst in observers for obs in olst]

    def stop(self):
        if not self.netw_thr:
            info('%s was already stopped' % self.__class__.__name__)
            return
        self.udp_sock.close()
        self.netw_thr.destroy()
        self.udp_sock = self.tcp_sock = self.netw_thr = None
        self.eng.detach_obs(self.on_frame)
        self.addr2conn = {}
        info('%s has been stopped' % self.__class__.__name__)

    def process_udp(self):
        try: dgram, conn = self.udp_sock.recvfrom(8192)
        except error: return
        self.on_udp_pck(dgram, conn)
        dgram = BinaryData.unpack(dgram)
        sender, payload = dgram[0], dgram[1:]
        self.read_cb(payload, conn)

    def on_udp_pck(self, dgram, conn): pass

    def destroy(self):
        self.stop()
        info('%s has been destroyed' % self.__class__.__name__)
        GameObject.destroy(self)
