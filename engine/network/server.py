from socket import socket, AF_INET, SOCK_DGRAM, gaierror
from json import load
from urllib2 import urlopen
from .network import AbsNetwork
from yyagl.library.panda.network import PandaConnectionListener


ConnectionListener = PandaConnectionListener


class Server(AbsNetwork):

    def __init__(self):
        AbsNetwork.__init__(self)
        self.conn_listener = self.tcp_socket = self.conn_cb = \
            self.listener_task = None
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
        try:
            sock.connect(('ya2.it', 0))
            local_addr = sock.getsockname()[0]
            public_addr = load(urlopen('http://httpbin.org/ip'))['origin']
            addr = local_addr + ' - ' + public_addr
        except gaierror:
            self.eng.log_mgr.log('no connection')
        self.eng.log('the server is up %s %s' % (public_addr, local_addr))

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

    def destroy(self):
        map(self.conn_reader.remove_connection, [conn[0] for conn in self.connections])
        self.conn_mgr.close_connection(self.tcp_socket)
        self.eng.remove_task(self.listener_task)
        self.conn_listener = self.tcp_socket = self.conn_cb = \
            self.listener_task = self.connections = None
        AbsNetwork.destroy(self)
        self.eng.log('the server has been destroyed')
