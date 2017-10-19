from panda3d.core import QueuedConnectionListener, PointerToConnection, NetAddress
from ..network import ConnectionListener


class PandaConnectionListener(ConnectionListener):

    def __init__(self, conn_mgr):
        self.conn_listener = QueuedConnectionListener(conn_mgr, num_threads=0)

    def add_conn(self, tcp_socket):
        return self.conn_listener.add_connection(tcp_socket)

    def conn_avail(self): return self.conn_listener.new_connection_available()

    def get_conn(self):
        new_conn = PointerToConnection()
        addr = NetAddress()
        conn = self.conn_listener.get_new_connection(
            rendezvous=PointerToConnection(), address=addr, new_connection=new_conn)
        if not conn: return
        return new_conn.p(), addr.get_ip_string()
