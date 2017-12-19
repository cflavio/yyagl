from sleekxmpp.jid import JID
import logging


try:
    from sleekxmpp import ClientXMPP
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


class XMPP(object):

    def __init__(self):
        self.xmpp = None

    def start(self, usr, pwd, on_ok, on_fail):
        logging.basicConfig(level=logging.DEBUG,
                            format='%(levelname)-8s %(message)s')
        self.xmpp = YorgClient(usr, pwd, on_ok, on_fail)
        self.xmpp.register_plugin('xep_0030') # Service Discovery
        self.xmpp.register_plugin('xep_0004') # Data Forms
        self.xmpp.register_plugin('xep_0060') # PubSub
        self.xmpp.register_plugin('xep_0199') # XMPP Ping
        if self.xmpp.connect(): self.xmpp.process()

    def send_connected(self):
        self.xmpp.send_connected()

    def destroy(self):
        if self.xmpp: self.xmpp.disconnect()
        self.xmpp = None


class YorgClient(ClientXMPP):

    def __init__(self, jid, password, on_ok, on_ko):
        ClientXMPP.__init__(self, jid, password)
        self.on_ok = on_ok
        self.add_event_handler('session_start', self.session_start)
        self.add_event_handler('failed_auth', on_ko)
        self.add_event_handler('message', self.on_message)

    def session_start(self, event):
        self.send_presence()
        self.get_roster()
        self.on_ok()

    def on_message(self, msg):
        for line in msg['body'].split():
            print JID(line).bare

    def send_connected(self):
        self.send_presence(
            pfrom=self.boundjid.full,
            pto='ya2_yorg@jabb3r.org')
        self.send_message(
            mfrom=self.boundjid.full,
            mto='ya2_yorg@jabb3r.org',
            mtype='chat',
            mbody='connected')
