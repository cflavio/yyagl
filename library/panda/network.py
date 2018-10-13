from panda3d.core import QueuedConnectionListener, QueuedConnectionManager, \
    QueuedConnectionReader, ConnectionWriter as P3DConnectionWriter, \
    NetDatagram, PointerToConnection, NetAddress
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator
from ..network import ConnectionListener, ConnectionMgr, ConnectionReader, \
    ConnectionWriter, WriteDatagram, DatagramIterator


class PandaConnectionListener(ConnectionListener):

    def __init__(self, conn_mgr):
        ConnectionListener.__init__(self)
        self.conn_listener = QueuedConnectionListener(conn_mgr.conn_mgr,
                                                      num_threads=0)

    def add_conn(self, tcp_socket):
        return self.conn_listener.add_connection(tcp_socket)

    def conn_avail(self): return self.conn_listener.new_connection_available()

    def get_conn(self):
        new_conn = PointerToConnection()
        addr = NetAddress()
        conn = self.conn_listener.get_new_connection(
            rendezvous=PointerToConnection(), address=addr,
            new_connection=new_conn)
        if not conn: return
        ip_string = addr.get_ip_string()
        if ip_string.startswith('::ffff:'): ip_string = ip_string[7:]
        return new_conn.p(), ip_string


class PandaConnectionMgr(ConnectionMgr):

    def __init__(self):
        ConnectionMgr.__init__(self)
        self.conn_mgr = QueuedConnectionManager()

    def open_TCP_server_rendezvous(self, port, backlog):
        return self.conn_mgr.open_TCP_server_rendezvous(port, backlog)

    def open_TCP_client_connection(self, hostname, port, timeout_ms):
        return self.conn_mgr.open_TCP_client_connection(hostname, port,
                                                        timeout_ms)

    def open_UDP_connection(self, port):
        return self.conn_mgr.open_UDP_connection(port)

    def close_connection(self, conn):
        return self.conn_mgr.close_connection(conn)


class PandaConnectionReader(ConnectionReader):

    def __init__(self, conn_mgr):
        ConnectionReader.__init__(self)
        self.conn_reader = QueuedConnectionReader(conn_mgr.conn_mgr,
                                                  num_threads=0)

    def data_available(self): return self.conn_reader.data_available()

    def add_conn(self, conn): self.conn_reader.add_connection(conn)

    def get(self):
        datagram = NetDatagram()
        if self.conn_reader.get_data(datagram): return datagram

    def remove_connection(self, conn):
        return self.conn_reader.remove_connection(conn)

    def destroy(self):
        self.conn_reader.shutdown()
        self.conn_reader = None


class PandaConnectionWriter(ConnectionWriter):

    def __init__(self, conn_mgr):
        ConnectionWriter.__init__(self)
        self.conn_writer = P3DConnectionWriter(conn_mgr.conn_mgr,
                                               num_threads=0)

    def send(self, msg, dst, addr=None):
        if addr is None: return self.conn_writer.send(msg.datagram, dst)
        else:
            return self.conn_writer.send(datagram=msg.datagram,
                                         connection=dst, address=addr)

    def destroy(self):
        self.conn_writer.shutdown()
        self.conn_writer = None


class PandaWriteDatagram(WriteDatagram):

    def __init__(self):
        WriteDatagram.__init__(self)
        self.datagram = PyDatagram()

    def add_bool(self, val): self.datagram.add_bool(val)

    def add_int(self, val): self.datagram.add_int32(val)

    def add_float(self, val): self.datagram.add_float32(val)

    def add_string(self, val): self.datagram.add_string(val)


class PandaDatagramIterator(DatagramIterator):

    def __init__(self, datagram):
        DatagramIterator.__init__(self)
        self._iter = PyDatagramIterator(datagram)

    def get_bool(self): return self._iter.get_bool()

    def get_int(self): return self._iter.get_int32()

    def get_float(self): return self._iter.get_float32()

    def get_string(self): return self._iter.get_string()
