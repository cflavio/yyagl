from panda3d.core import QueuedConnectionListener, PointerToConnection, \
    NetAddress
from .network import AbsNetwork


class Server(AbsNetwork):

    def __init__(self):
        AbsNetwork.__init__(self)
        self.c_listener = None
        self.tcp_socket = None
        self.connection_cb = None
        self.listener_tsk = None
        self.connections = []

    def start(self, reader_cb, connection_cb):
        AbsNetwork.start(self, reader_cb)
        self.connection_cb = connection_cb
        self.c_listener = QueuedConnectionListener(self.c_mgr, 0)
        self.connections = []
        self.tcp_socket = self.c_mgr.open_TCP_server_rendezvous(9099, 1000)
        self.c_listener.add_connection(self.tcp_socket)
        self.listener_tsk = self.eng.add_task(self.tsk_listener, -39)
        self.eng.log_mgr.log('the server is up')

    def tsk_listener(self, task):
        if not self.c_listener.newConnectionAvailable():
            return task.cont
        net_address = NetAddress()
        new_connection = PointerToConnection()
        args = PointerToConnection(), net_address, new_connection
        if not self.c_listener.get_new_connection(*args):
            return task.cont
        self.connections.append(new_connection.p())
        self.c_reader.add_connection(self.connections[-1])
        self.connection_cb(net_address.get_ip_string())
        msg = 'received a connection from ' + net_address.getIpString()
        self.eng.log_mgr.log(msg)
        return task.cont

    def _actual_send(self, datagram, receiver):
        dests = [cln for cln in self.connections if cln == receiver] \
            if receiver else self.connections
        map(lambda cln: self.c_writer.send(datagram, cln), dests)

    def destroy(self):
        AbsNetwork.destroy(self)
        map(self.c_reader.remove_connection, self.connections)
        self.c_mgr.close_connection(self.tcp_socket)
        taskMgr.remove(self.listener_tsk)
        self.c_listener = self.tcp_socket = self.connection_cb = \
            self.listener_tsk = self.connections = None
        self.eng.log_mgr.log('the server has been destroyed')
