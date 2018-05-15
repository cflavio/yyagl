from decimal import Decimal
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

    rate = .1

    def __init__(self):
        GameObject.__init__(self)
        self.conn_mgr = None
        self.conn_reader = None
        self.conn_reader_udp = None
        self.conn_writer = None
        self.read_cb = None
        self.addr2conn = {}

    def start(self, read_cb):
        self.conn_mgr = ConnectionMgr()
        self.conn_reader = ConnectionReader(self.conn_mgr)
        self.conn_writer = ConnectionWriter(self.conn_mgr)
        self.eng.attach_obs(self.on_frame, 1)
        self.read_cb = read_cb

    def send(self, data_lst, receiver=None):
        datagram = WriteDatagram()
        types = {bool: 'B', int: 'I', float: 'F', str: 'S', unicode: 'S'}
        datagram.add_string(''.join(types[type(part)] for part in data_lst))
        type2mth = {
            bool: datagram.add_bool, int: datagram.add_int,
            float: datagram.add_float, str: datagram.add_string,
            unicode: datagram.add_string}
        map(lambda data: type2mth[type(data)](data), data_lst)
        self._actual_send(datagram, receiver)

    def on_frame(self):
        self.process_udp()
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

    def _fix_payload(self, payload):
        ret = {}
        ret['sender'] = payload['sender']
        def __fix(elm):
            return float(elm) if type(elm) == Decimal else elm
        ret['payload'] = [__fix(payl) for payl in payload['payload']]
        return ret

    @property
    def is_active(self):
        return self.on_frame in [obs.mth for obslist in self.eng.event.observers.values() for obs in obslist]

    def stop(self):
        if self.udp_sock:
            self.eng.detach_obs(self.on_frame)
            self.conn_reader.destroy()
            self.conn_writer.destroy()
            self.udp_sock.close()
            self.addr2conn = {}
            self.udp_sock = self.conn_mgr = self.conn_reader = self.conn_writer = None

    def destroy(self):
        self.stop()
        GameObject.destroy(self)
