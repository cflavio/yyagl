from panda3d.core import QueuedConnectionManager, QueuedConnectionReader, \
    ConnectionWriter, NetDatagram
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator
from yyagl.gameobject import GameObject


class AbsNetwork(GameObject):

    def __init__(self):
        self.c_mgr = None
        self.c_reader = None
        self.c_writer = None
        self.reader_cb = None

    def start(self, reader_cb):
        self.c_mgr = QueuedConnectionManager()
        self.c_reader = QueuedConnectionReader(self.c_mgr, 0)
        self.c_writer = ConnectionWriter(self.c_mgr, 0)
        self.eng.attach_obs(self.on_frame, 1)
        self.reader_cb = reader_cb

    def send(self, data, receiver=None):
        datagram = PyDatagram()
        types = {bool: 'B', int: 'I', float: 'F', str: 'S'}
        datagram.add_string(''.join(types[type(part)] for part in data))
        meths = {
            bool: datagram.add_bool, int: datagram.add_int64,
            float: datagram.add_float64, str: datagram.add_string}
        map(lambda part: meths[type(part)](part), data)
        self._actual_send(datagram, receiver)

    def on_frame(self):
        if not self.c_reader.data_available():
            return
        datagram = NetDatagram()
        if not self.c_reader.get_data(datagram):
            return
        _iter = PyDatagramIterator(datagram)
        meths = {'B': _iter.get_bool, 'I': _iter.get_int64,
                 'F': _iter.get_float64, 'S': _iter.get_string}
        msg = [meths[c]() for c in _iter.get_string()]
        self.reader_cb(msg, datagram.get_connection())

    def register_cb(self, callback):
        self.reader_cb = callback

    @property
    def is_active(self):
        return self.on_frame in [obs[0] for obs in self.eng.event.observers]

    def destroy(self):
        self.eng.detach_obs(self.on_frame)
