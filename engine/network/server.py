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
        self.eng.log('the server is up')

    def task_listener(self, task):
        if not self.conn_listener.conn_avail(): return task.cont
        conn, addr = self.conn_listener.get_conn()
        if not conn: return task.cont
        self.connections += [conn]
        self.conn_reader.add_conn(self.connections[-1])
        self.conn_cb(addr)
        msg = 'received a connection from ' + addr
        self.eng.log(msg)
        return task.cont

    def _actual_send(self, datagram, receiver=None):
        receivers = [cln for cln in self.connections if cln == receiver]
        dests = receivers if receiver else self.connections
        map(lambda cln: self.conn_writer.send(datagram, cln), dests)

    def destroy(self):
        AbsNetwork.destroy(self)
        map(self.conn_reader.remove_connection, self.connections)
        self.conn_mgr.close_connection(self.tcp_socket)
        self.eng.remove_task(self.listener_task)
        self.conn_listener = self.tcp_socket = self.conn_cb = \
            self.listener_task = self.connections = None
        self.eng.log('the server has been destroyed')
