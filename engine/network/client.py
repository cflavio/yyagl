from socket import socket, AF_INET, SOCK_DGRAM, gaierror, error, SOCK_STREAM, \
    SOL_SOCKET, SO_REUSEADDR
from select import select
from struct import Struct
from Queue import Queue, Empty
from threading import Thread, Lock
from json import load
from urllib2 import urlopen
from simpleubjson import encode, decode
from .network import AbsNetwork, NetworkError


class ClientThread(Thread):

    def __init__(self, srv_addr, eng):
        Thread.__init__(self)
        self.eng = eng
        self.is_running = True
        self.tcp_sock = socket(AF_INET, SOCK_STREAM)
        self.tcp_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.tcp_sock.connect((srv_addr, 9099))
        self.msgs = Queue()
        self.size_struct = Struct('!I')

    def run(self):
        while self.is_running:
            try:
                readable, writable, exceptional = select(
                    [self.tcp_sock], [self.tcp_sock], [self.tcp_sock], 1)
                for s in readable:
                    data = self.recv_one_message(s)
                    if data:
                        self.eng.cb_mux.add_cb(self.read_cb, [dict(decode(data))['payload'], s])
                for s in writable:
                    try:
                        msg = self.msgs.get_nowait()
                        s.sendall(self.size_struct.pack(len(msg)))
                        s.sendall(msg)
                    except Empty: pass
                for s in exceptional: print 'exception', s.getpeername()
            except error as e: print e

    def send_msg(self, msg): self.msgs.put(msg)

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

    def destroy(self):
        self.is_running = False
        self.tcp_sock.close()


class Client(AbsNetwork):

    def __init__(self):
        AbsNetwork.__init__(self)
        self.udp_sock = None

    def start(self, read_cb, srv_addr, my_addr):
        AbsNetwork.start(self, read_cb)
        self.srv_addr = srv_addr
        sock = socket(AF_INET, SOCK_DGRAM)
        sock.connect(('ya2.it', 8080))
        self.local_addr = sock.getsockname()[0]
        self.public_addr = load(urlopen('http://httpbin.org/ip', timeout=3))['origin']
        self.udp_sock = socket(AF_INET, SOCK_DGRAM)
        self.udp_sock.setblocking(0)
        self.my_addr = my_addr
        self.client_thread = ClientThread(srv_addr, self.eng)
        self.client_thread.start()
        self.client_thread.read_cb = read_cb
        self.read_cb = read_cb
        self.eng.log('the client is up')

    def register_cb(self, callback):
        self.read_cb = callback
        self.client_thread.read_cb = callback

    def send_udp(self, data_lst, receiver=None):
        receiver = receiver if receiver else self.srv_addr
        payload = {'sender': self.my_addr, 'payload': data_lst}
        self.udp_sock.sendto(encode(payload), (receiver, 9099))

    def process_udp(self):
        try:
            payload, addr = self.udp_sock.recvfrom(8192)
            payload = self._fix_payload(dict(decode(payload)))
            self.read_cb(payload['payload'], payload['sender'])
        except error: pass

    def _actual_send(self, datagram, receiver=None):
        self.client_thread.send_msg(datagram)

    def stop(self):
        self.eng.log('the client has been stopped')
        if self.udp_sock:
            self.udp_sock.close()
            self.client_thread.destroy()
        else: self.eng.log('the client was already stopped')
        AbsNetwork.stop(self)

    def destroy(self):
        self.stop()
        self.eng.log('the client has been destroyed')
        AbsNetwork.destroy(self)
