from socket import error, socket, AF_INET, SOCK_DGRAM
from queue import Queue, Empty
from bson import dumps
from yyagl.engine.network.network import AbsNetwork, ConnectionError, NetworkThread


class ClientThread(NetworkThread):

    def __init__(self, srv_addr, eng, port):
        self.srv_addr = srv_addr
        NetworkThread.__init__(self, eng, port)
        self.msgs = Queue()
        self.rpc_ret = Queue()

    def _configure_socket(self):
        self.tcp_sock.connect((self.srv_addr, self.port))

    def _rpc_cb(self, dct, sock):
        self.rpc_ret.put(dct['result'])

    def _queue(self, sock):
        return self.msgs

    def send_msg(self, msg, receiver=None): self.msgs.put(msg)

    def do_rpc(self, funcname, args, kwargs):
        msg = {'is_rpc': True, 'payload': [funcname, args, kwargs]}
        self.msgs.put(dumps(msg))
        return self.rpc_ret.get()


class Client(AbsNetwork):

    def __init__(self, port, srv_addr):
        AbsNetwork.__init__(self, port)
        self.srv_addr = srv_addr
        self._functions = []

    def start(self, read_cb):
        return AbsNetwork.start(self, read_cb)

    def _bld_netw_thr(self):
        srv, port = self.srv_addr.split(':')
        return ClientThread(srv, self.eng, int(port))

    def _configure_udp(self): pass

    def send_udp(self, data_lst, sender):
        dgram = {'sender': sender, 'payload': data_lst}
        host, port = self.srv_addr.split(':')
        self.udp_sock.sendto(dumps(dgram), (host, int(port)))

    def register_rpc(self, funcname): self._functions += [funcname]

    def unregister_rpc(self, funcname): self._functions.remove(funcname)

    def __getattr__(self, attr):
        if attr not in self._functions: raise AttributeError(attr)

        def do_rpc(*args, **kwargs):
            return self.netw_thr.do_rpc(attr, args, kwargs)
        return do_rpc
