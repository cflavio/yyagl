class ConnectionListener(object):

    def __init__(self, conn_mgr): pass

    def add_conn(self, tcp_socket): pass

    def conn_avail(self): pass

    def get_conn(self): pass


class ConnectionMgr(object):

    def __init__(self): pass

    def open_tcp_server_rendezvous(self, port, backlog): pass

    def open_tcp_client_connection(self, hostname, port, timeout_ms): pass

    def open_udp_connection(self, port): pass


class ConnectionReader(object):

    def __init__(self, conn_mgr): pass

    def data_available(self): pass

    def add_conn(self, conn): pass

    def get(self): pass

    def destroy(self): pass


class ConnectionWriter(object):

    def __init__(self, conn_mgr): pass

    def send(self, msg, dst, addr=None): pass

    def destroy(self): pass


class WriteDatagram(object):

    def __init__(self): pass

    def add_bool(self, val): pass

    def add_int(self, val): pass

    def add_float(self, val): pass

    def add_string(self, val): pass


class DatagramIterator(object):

    def __init__(self, datagram): pass

    def get_bool(self): pass

    def get_int(self): pass

    def get_float(self): pass

    def get_string(self): pass
