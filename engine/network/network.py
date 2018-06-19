from simpleubjson import encode, decode
from decimal import Decimal
from yyagl.gameobject import GameObject


class NetworkError(Exception): pass


class ConnectionError(Exception): pass


class AbsNetwork(GameObject):

    rate = .1

    def __init__(self):
        GameObject.__init__(self)
        self.read_cb = None
        self.addr2conn = {}

    def start(self, read_cb):
        self.eng.attach_obs(self.on_frame, 1)
        self.read_cb = read_cb

    def send(self, data_lst, receiver=None):
        self._actual_send(encode({'payload': data_lst}), receiver)

    def on_frame(self): self.process_udp()

    def register_cb(self, callback): self.read_cb = callback

    def _fix_payload(self, payload):
        ret = {'sender': payload['sender']}
        def __fix(elm):
            return float(elm) if type(elm) == Decimal else elm
        ret['payload'] = [__fix(payl) for payl in payload['payload']]
        return ret

    @property
    def is_active(self):
        return self.on_frame in [obs.mth for obslist in self.eng.event.observers.values() for obs in obslist]

    def stop(self):
        if not self.udp_sock: return
        self.eng.detach_obs(self.on_frame)
        self.udp_sock.close()
        self.addr2conn = {}
        self.udp_sock = None

    def destroy(self):
        self.stop()
        GameObject.destroy(self)
