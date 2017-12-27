import logging
from yyagl.observer import Subject


try:
    from sleekxmpp import ClientXMPP
    from sleekxmpp.jid import JID
except ImportError:  # sleekxmpp requires openssl 1.0.2
    print 'OpenSSL 1.0.2 not detected'
    class ClientXMPP:
        def __init__(self, jid, password): taskMgr.doMethodLater(.5, lambda tsk: self.on_ok(), 'on ok')
        def add_event_handler(self, msg, cb): pass
        def register_plugin(self, plugin): pass
        def connect(self): pass
        def send_presence(self, pfrom, pto): pass
        def send_message(self, mfrom, mto, mtype, mbody): pass
        def disconnect(self): pass


class XMPP(Subject):

    def __init__(self):
        Subject.__init__(self)
        self.xmpp = None
        self.users = []

    def start(self, usr, pwd, on_ok, on_fail):
        logging.basicConfig(level=logging.DEBUG,
                            format='%(levelname)-8s %(message)s')
        self.xmpp = YorgClient(usr, pwd, on_ok, on_fail, self)
        self.xmpp.register_plugin('xep_0030') # Service Discovery
        self.xmpp.register_plugin('xep_0004') # Data Forms
        self.xmpp.register_plugin('xep_0060') # PubSub
        self.xmpp.register_plugin('xep_0199') # XMPP Ping
        if self.xmpp.connect(): self.xmpp.process()

    def send_connected(self):
        self.xmpp.send_connected()

    def disconnect(self):
        if self.xmpp:
            self.xmpp.disconnect()
            self.xmpp = self.xmpp.destroy()

    def destroy(self):
        self.disconnect()
        Subject.destroy(self)


class YorgClient(ClientXMPP):

    def __init__(self, jid, password, on_ok, on_ko, xmpp):
        self.xmpp = xmpp
        ClientXMPP.__init__(self, jid, password)
        self.on_ok = on_ok
        self.on_ko = on_ko
        self.add_event_handler('session_start', self.session_start)
        self.add_event_handler('failed_auth', on_ko)
        self.add_event_handler('message', self.on_message)

    def session_start(self, event):
        self.send_presence()
        self.get_roster()
        self.on_ok()

    def on_message(self, msg):
        self.xmpp.users = []
        for line in msg['body'].split():
            if JID(line).bare != self.boundjid.bare:
                self.xmpp.users += [line]

        # generate some random users for development
        for n in range(40):
            from random import choice
            from string import ascii_lowercase
            nn = ''
            for i in range(choice(range(5, 16))):
                for j in choice(ascii_lowercase):
                    nn += j
            self.xmpp.users += [nn]

        self.xmpp.users += [self.boundjid.bare]
        self.xmpp.notify('on_users')

    def send_connected(self):
        self.send_presence(
            pfrom=self.boundjid.full,
            pto='ya2_yorg@jabb3r.org')
        self.send_message(
            mfrom=self.boundjid.full,
            mto='ya2_yorg@jabb3r.org',
            mtype='chat',
            mbody='connected')

    def destroy(self):
        self.del_event_handler('session_start', self.session_start)
        self.del_event_handler('failed_auth', self.on_ko)
        self.del_event_handler('message', self.on_message)
