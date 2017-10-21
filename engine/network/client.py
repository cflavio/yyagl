from .network import AbsNetwork


class ClientError(Exception):
    pass


class Client(AbsNetwork):

    def __init__(self):
        AbsNetwork.__init__(self)
        self.conn = None

    def start(self, read_cb, srv_addr):
        AbsNetwork.start(self, read_cb)
        self.conn = self.conn_mgr.open_TCP_client_connection(
            hostname=srv_addr, port=9099, timeout_ms=3000)
        if not self.conn: raise ClientError
        self.conn_reader.add_conn(self.conn)
        self.eng.log('the client is up')

    def _actual_send(self, datagram, receiver=None):
        self.conn_writer.send(datagram, self.conn)

    def destroy(self):
        self.conn_mgr.close_connection(self.conn)
        self.conn = None
        self.eng.log('the client has been destroyed')
        AbsNetwork.destroy(self)
