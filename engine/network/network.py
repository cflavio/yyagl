from panda3d.core import QueuedConnectionManager, QueuedConnectionReader, \
    ConnectionWriter, NetDatagram, NetAddress
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator
from yyagl.gameobject import GameObject
from yyagl.library.panda.network import PandaConnectionMgr, \
    PandaConnectionReader, PandaConnectionWriter, PandaWriteDatagram, \
    PandaDatagramIterator


ConnectionMgr = PandaConnectionMgr
ConnectionReader = PandaConnectionReader
ConnectionWriter = PandaConnectionWriter
WriteDatagram = PandaWriteDatagram
DatagramIterator = PandaDatagramIterator


class NetworkError(Exception):
    pass


class AbsNetwork(GameObject):

    def __init__(self):
        GameObject.__init__(self)
        self.conn_mgr = None
        self.conn_reader = None
        self.conn_writer = None
        self.read_cb = None

    def start(self, read_cb):
        self.conn_mgr = ConnectionMgr()
        self.conn_reader = ConnectionReader(self.conn_mgr)
        self.conn_writer = ConnectionWriter(self.conn_mgr)
        self.conn_udp = self.conn_mgr.open_UDP_connection(9099)
        if not self.conn_udp: raise NetworkError
        self.conn_reader.add_conn(self.conn_udp)
        self.eng.attach_obs(self.on_frame, 1)
        self.read_cb = read_cb

    def send(self, data_lst, receiver=None):
        datagram = WriteDatagram()
        types = {bool: 'B', int: 'I', float: 'F', str: 'S'}
        datagram.add_string(''.join(types[type(part)] for part in data_lst))
        type2mth = {
            bool: datagram.add_bool, int: datagram.add_int,
            float: datagram.add_float, str: datagram.add_string}
        map(lambda data: type2mth[type(data)](data), data_lst)
        self._actual_send(datagram, receiver)

    def _actual_send_udp(self, datagram, receiver=None):
        addr = NetAddress()
        addr.set_host(receiver, 9099)
        self.conn_writer.send(datagram, self.conn_udp, addr)

    def send_udp(self, data_lst, receiver=None):
        datagram = WriteDatagram()
        my_addr = self.my_addr if hasattr(self, 'my_addr') else 'server'
        data_lst = data_lst + [my_addr]
        types = {bool: 'B', int: 'I', float: 'F', str: 'S'}
        datagram.add_string(''.join(types[type(part)] for part in data_lst))
        type2mth = {
            bool: datagram.add_bool, int: datagram.add_int,
            float: datagram.add_float, str: datagram.add_string}
        map(lambda data: type2mth[type(data)](data), data_lst)
        self._actual_send_udp(datagram, receiver)

    def on_frame(self):
        if not self.conn_reader.data_available(): return
        datagram = self.conn_reader.get()
        if not datagram: return
        _iter = DatagramIterator(datagram)
        char2mth = {'B': _iter.get_bool, 'I': _iter.get_int,
                 'F': _iter.get_float, 'S': _iter.get_string}
        msg = [char2mth[c]() for c in _iter.get_string()]
        self.read_cb(msg, datagram.get_connection())

    def register_cb(self, callback):
        self.read_cb = callback

    @property
    def is_active(self):
        return self.on_frame in [obs.mth for obslist in self.eng.event.observers.values() for obs in obslist]

    def destroy(self):
        self.eng.detach_obs(self.on_frame)
        self.conn_reader.destroy()
        self.conn_writer.destroy()
        self.conn_mgr = self.conn_reader = self.conn_writer = None
        GameObject.destroy(self)
