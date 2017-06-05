from .network import AbsNetwork
from ...singleton import Singleton


class ClientError(Exception):
    pass


class Client(AbsNetwork):
    __metaclass__ = Singleton

    def __init__(self):
        AbsNetwork.__init__(self)
        self.conn = None

    def start(self, reader_cb, server_address):
        AbsNetwork.start(self, reader_cb)
        args = server_address, 9099, 3000
        self.conn = self.c_mgr.open_TCP_client_connection(*args)
        if not self.conn:
            raise ClientError
        self.c_reader.add_connection(self.conn)
        LogMgr().log('the client is up')

    def _actual_send(self, datagram, receiver):
        self.c_writer.send(datagram, self.conn)

    def destroy(self):
        AbsNetwork.destroy(self)
        self.c_mgr.close_connection(self.conn)
        LogMgr().log('the client has been destroyed')
