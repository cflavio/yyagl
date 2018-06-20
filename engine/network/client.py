from socket import socket, AF_INET, SOCK_DGRAM, gaierror, error, SOCK_STREAM, \
    SOL_SOCKET, SO_REUSEADDR
from select import select
from struct import Struct, error as unpack_error
from Queue import Queue, Empty
from threading import Thread, Lock
from json import load
from urllib2 import urlopen
from simpleubjson import encode, decode
from .network import AbsNetwork, NetworkError, ConnectionError, NetworkThread


class ClientThread(NetworkThread):

    def __init__(self, srv_addr, eng):
        self.srv_addr = srv_addr
        NetworkThread.__init__(self, eng)
        self.msgs = Queue()
        self.rpc_ret = Queue()

    def _configure_socket(self):
        self.tcp_sock.connect((self.srv_addr, 9099))

    def _process_read(self, s):
        try:
            data = self.recv_one_message(s)
            if data:
                d = dict(decode(data))
                if 'is_rpc' in d: self.rpc_ret.put(d['result'])
                else:
                    self.eng.cb_mux.add_cb(self.read_cb, [d['payload'], s])
        except ConnectionError as e:
            print e
            self.connections.remove(s)

    def _process_write(self, s):
        try:
            msg = self.msgs.get_nowait()
            s.sendall(self.size_struct.pack(len(msg)))
            s.sendall(msg)
        except Empty: pass

    def send_msg(self, msg): self.msgs.put(msg)

    def do_rpc(self, funcname, args, kwargs):
        msg = {'is_rpc': True, 'payload': [funcname, args, kwargs]}
        self.msgs.put(encode(msg))
        return self.rpc_ret.get()


class Client(AbsNetwork):

    def __init__(self):
        AbsNetwork.__init__(self)
        self.udp_sock = None
        self._functions = []

    def start(self, read_cb, srv_addr, my_addr):
        self.srv_addr = srv_addr
        self.my_addr = my_addr
        AbsNetwork.start(self, read_cb)

    def _build_network_thread(self):
        return ClientThread(self.srv_addr, self.eng)

    def _configure_udp(self): pass

    def send_udp(self, data_lst, receiver=None):
        receiver = receiver if receiver else self.srv_addr
        payload = {'sender': self.my_addr, 'payload': data_lst}
        self.udp_sock.sendto(encode(payload), (receiver, 9099))

    def register_rpc(self, funcname): self._functions += [funcname]

    def unregister_rpc(self, funcname): self._functions.remove(funcname)

    def __getattr__(self, attr):
        if attr not in self._functions: raise AttributeError(attr)
        def do_rpc(*args, **kwargs):
            return self.network_thr.do_rpc(attr, args, kwargs)
        return do_rpc

    def process_udp(self):
        try:
            payload, addr = self.udp_sock.recvfrom(8192)
            payload = self._fix_payload(dict(decode(payload)))
            self.read_cb(payload['payload'], payload['sender'])
        except error: pass

    def _actual_send(self, datagram, receiver=None):
        self.network_thr.send_msg(datagram)
