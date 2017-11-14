from .network import AbsNetwork


class ClientError(Exception):
    pass


class Client(AbsNetwork):

    def __init__(self):
        AbsNetwork.__init__(self)
        self.conn = None
        self.conn_udp = None

    def start(self, read_cb, srv_addr):
        AbsNetwork.start(self, read_cb)
        self.srv_addr = srv_addr
        self.conn = self.conn_mgr.open_TCP_client_connection(
            hostname=srv_addr, port=9099, timeout_ms=3000)
        if not self.conn: raise ClientError
        self.my_addr = self.conn.get_address().get_ip_string() + ':' + str(self.conn.get_address().get_port())
        self.conn_reader.add_conn(self.conn)
        self.eng.log('the client is up')

    def send_udp(self, data_lst, receiver=None):
        AbsNetwork.send_udp(self, data_lst, receiver if receiver else self.srv_addr)

    def _actual_send(self, datagram, receiver=None):
        self.conn_writer.send(datagram, self.conn)

    def destroy(self):
        self.conn_mgr.close_connection(self.conn)
        self.conn = None
        self.conn_mgr.close_connection(self.conn_udp)
        self.conn_udp = None
        self.eng.log('the client has been destroyed')
        AbsNetwork.destroy(self)
