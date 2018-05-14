from socket import socket, AF_INET, SOCK_DGRAM, gaierror, error
from json import load
from pickle import loads, dumps
from urllib2 import urlopen
from .network import AbsNetwork
from yyagl.library.panda.network import PandaConnectionListener


ConnectionListener = PandaConnectionListener


class Server(AbsNetwork):

    def __init__(self):
        AbsNetwork.__init__(self)
        self.conn_listener = self.tcp_socket = self.conn_cb = \
            self.listener_task = self.public_addr = self.local_addr = None
        self.connections = []

    def start(self, read_cb, conn_cb):
        AbsNetwork.start(self, read_cb)
        self.conn_cb = conn_cb
        self.conn_listener = ConnectionListener(self.conn_mgr)
        self.connections = []
        self.tcp_socket = self.conn_mgr.open_TCP_server_rendezvous(port=9099, backlog=1000)
        self.conn_listener.add_conn(self.tcp_socket)
        self.listener_task = self.eng.add_task(self.task_listener, self.eng.network_priority)
        sock = socket(AF_INET, SOCK_DGRAM)
        sock.connect(('ya2.it', 8080))
        self.local_addr = sock.getsockname()[0]
        self.public_addr = load(urlopen('http://httpbin.org/ip', timeout=3))['origin']
        self.udp_sock = socket(AF_INET, SOCK_DGRAM)
        self.udp_sock.bind(('', 9099))
        self.udp_sock.setblocking(0)

        self.eng.log('the server is up %s %s' % (self.public_addr, self.local_addr))

    def task_listener(self, task):
        if not self.conn_listener.conn_avail(): return task.cont
        conn, addr = self.conn_listener.get_conn()
        if not conn: return task.cont
        self.connections += [(conn, addr)]
        self.conn_reader.add_conn(self.connections[-1][0])
        self.conn_cb(addr)
        msg = 'received a connection from ' + addr
        self.eng.log(msg)
        return task.cont

    def _actual_send(self, datagram, receiver=None):
        receivers = [cln for cln in [conn[0] for conn in self.connections] if cln == receiver]
        dests = receivers if receiver else [conn[0] for conn in self.connections]
        map(lambda cln: self.conn_writer.send(datagram, cln), dests)

    def process_udp(self):
        try:
            payload, client_address = self.udp_sock.recvfrom(8192)
        except error: return
        payload = loads(payload)
        sender = payload['sender']
        if sender not in self.addr2conn:
            self.addr2conn[sender] = client_address
        self.read_cb(payload['payload'], client_address)

    def send_udp(self, data_lst, receiver):
        if receiver not in self.addr2conn: return
        payload = {}
        my_addr = self.my_addr if hasattr(self, 'my_addr') else 'server'
        payload['sender'] = my_addr
        payload['payload'] = data_lst
        self.udp_sock.sendto(dumps(payload), self.addr2conn[receiver])

    def stop(self):
        if self.tcp_socket:
            map(self.conn_reader.remove_connection, [conn[0] for conn in self.connections])
            self.conn_mgr.close_connection(self.tcp_socket)
            self.eng.remove_task(self.listener_task)
            self.udp_sock.close()
            self.conn_listener = self.tcp_socket = self.conn_cb = \
                self.listener_task = self.connections = None
        else: self.eng.log('the server was already stopped')
        AbsNetwork.stop(self)
        self.eng.log('the server has been stopped')

    def destroy(self):
        AbsNetwork.destroy(self)
        self.eng.log('the server has been destroyed')
