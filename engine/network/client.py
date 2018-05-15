from socket import socket, AF_INET, SOCK_DGRAM, gaierror, error
from json import load
from urllib2 import urlopen
from simpleubjson import encode, decode
from .network import AbsNetwork, NetworkError


class Client(AbsNetwork):

    def __init__(self):
        AbsNetwork.__init__(self)
        self.conn = None

    def start(self, read_cb, srv_addr, my_addr):
        AbsNetwork.start(self, read_cb)
        self.srv_addr = srv_addr
        sock = socket(AF_INET, SOCK_DGRAM)
        sock.connect(('ya2.it', 8080))
        self.local_addr = sock.getsockname()[0]
        self.public_addr = load(urlopen('http://httpbin.org/ip', timeout=3))['origin']
        self.udp_sock = socket(AF_INET, SOCK_DGRAM)
        self.udp_sock.setblocking(0)
        self.conn = self.conn_mgr.open_TCP_client_connection(
            hostname=srv_addr, port=9099, timeout_ms=3000)
        if not self.conn: raise NetworkError
        self.my_addr = my_addr
        self.conn_reader.add_conn(self.conn)
        self.eng.log('the client is up')

    def send_udp(self, data_lst, receiver=None):
        receiver = receiver if receiver else self.srv_addr
        payload = {'sender': self.my_addr, 'payload': data_lst}
        self.udp_sock.sendto(encode(payload), (receiver, 9099))

    def process_udp(self):
        try:
            payload, client_address = self.udp_sock.recvfrom(8192)
            payload = self._fix_payload(dict(decode(payload)))
            sender = payload['sender']
            self.read_cb(payload['payload'], sender)
        except error: pass

    def _actual_send(self, datagram, receiver=None):
        self.conn_writer.send(datagram, self.conn)

    def stop(self):
        self.eng.log('the client has been stopped')
        if self.conn:
            self.conn_mgr.close_connection(self.conn)
            self.conn = None
            self.udp_sock.close()
        else: self.eng.log('the client was already stopped')
        AbsNetwork.stop(self)

    def destroy(self):
        self.stop()
        self.eng.log('the client has been destroyed')
        AbsNetwork.destroy(self)
