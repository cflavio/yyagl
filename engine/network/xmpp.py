from threading import Lock
from yyagl.observer import Subject
import logging


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


class CallbackMux():
    # this is a sort of "multiplexer" i.e. it manages callbacks from threads
    # and redirect them to the main thread (this prevents deadlocks)

    def __init__(self):
        self.lock = Lock()
        self.callbacks = []
        taskMgr.add(self.process_callbacks, 'processing callbacks')

    def add_cb(self, func, args):
        with self.lock: self.callbacks += [(func, args)]

    def process_callbacks(self, task):
        with self.lock:
            callbacks = self.callbacks[:]
            self.callbacks = []
        for func, args in callbacks: func(*args)
        return task.cont


class User(object):

    def __init__(self, name_full, is_supporter, is_in_yorg, xmpp):
        self.name_full = name_full
        self.name = JID(name_full).bare
        self.is_supporter = is_supporter
        self.is_in_yorg = is_in_yorg
        self.xmpp = xmpp

    @property
    def is_friend(self):
        return self.name in self.xmpp.friends


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
        self.xmpp.register_plugin('xep_0045') # Multi-User Chat
        #self.xmpp.auto_authorize = False
        #self.xmpp.auto_subscribe = False
        if self.xmpp.connect(): self.xmpp.process()

    def send_connected(self):
        self.xmpp.send_connected()

    def disconnect(self):
        if self.xmpp:
            self.xmpp.disconnect()
            self.xmpp = self.xmpp.destroy()

    @property
    def friends(self):
        return self.xmpp.friends

    def is_friend(self, name):
        return name in self.xmpp.friends

    def destroy(self):
        self.disconnect()
        Subject.destroy(self)


class YorgClient(ClientXMPP):

    def __init__(self, jid, password, on_ok, on_ko, xmpp):
        self.xmpp = xmpp
        self.presences_sent = []
        ClientXMPP.__init__(self, jid, password)
        self.on_ok = on_ok
        self.on_ko = on_ko
        self.cb_mux = CallbackMux()
        self.add_event_handler('session_start', lambda msg: self.dispatch_msg('session_start', msg))
        self.add_event_handler('failed_auth', lambda msg: self.dispatch_msg('failed_auth', msg))
        self.add_event_handler('message', lambda msg: self.dispatch_msg('message', msg))
        self.add_event_handler('groupchat_message', lambda msg: self.dispatch_msg('groupchat_message', msg))
        self.add_event_handler('presence_subscribe', lambda msg: self.dispatch_msg('subscribe', msg))
        self.add_event_handler('presence_subscribed', lambda msg: self.dispatch_msg('subscribed', msg))
        self.add_event_handler('presence_available', lambda msg: self.dispatch_msg('presence_available', msg))
        self.add_event_handler('presence_unavailable', lambda msg: self.dispatch_msg('presence_unavailable', msg))

    def dispatch_msg(self, code, msg):
        if code == 'session_start': self.cb_mux.add_cb(self.session_start, [msg])
        if code == 'failed_auth': self.cb_mux.add_cb(self.on_ko, [msg])
        if code == 'message': self.cb_mux.add_cb(self.on_message, [msg])
        if code == 'groupchat_message': self.cb_mux.add_cb(self.on_groupchat_message, [msg])
        if code == 'subscribe': self.cb_mux.add_cb(self.on_subscribe, [msg])
        if code == 'subscribed': self.cb_mux.add_cb(self.on_subscribed, [msg])
        if code == 'presence_available': self.cb_mux.add_cb(self.on_presence_available, [msg])
        if code == 'presence_unavailable': self.cb_mux.add_cb(self.on_presence_unavailable, [msg])

    def session_start(self, event):
        self.send_presence()
        self.get_roster()
        logging.info(self.client_roster)
        self.on_ok()
        res = self['xep_0030'].get_items(jid=self.xmpp.xmpp.boundjid.server, iterator=True)
        for itm in res['disco_items']:
            if 'conference' in itm['jid']:
                self.xmpp.xmpp.conf_srv = itm['jid']

    @property
    def friends(self):
        friends = self.client_roster.keys()
        return friends

    def on_subscribe(self, msg):
        self.xmpp.notify('on_user_subscribe', msg['from'])
        logging.info('subscribe ' + str(self.client_roster))
        self.xmpp.notify('on_users')

    def on_subscribed(self, msg):
        logging.info('subscribed ' + str(self.client_roster))

    def on_presence_available(self, msg):
        if str(msg['from']) not in [usr.name_full for usr in self.xmpp.users]:
            self.xmpp.users += [User(msg['from'], 0, True, self.xmpp)]
            # TODO: create with is_in_yorg == False and use a stanza for
            # setting is_in_yorg = True
        self.sort_users()
        if msg['from'].bare != self.xmpp.xmpp.boundjid.bare and msg['from'] not in self.presences_sent:
            self.presences_sent += [msg['from']]
            self.xmpp.xmpp.send_presence(
                pfrom=self.xmpp.xmpp.boundjid.full,
                pto=msg['from'])
        self.xmpp.notify('on_presence_available', msg)

    def on_presence_unavailable(self, msg):
        usr = [_usr for _usr in self.xmpp.users if _usr.name==msg['from'].bare]
        if usr:  # we receive unavailable for nonlogged users at the beginning
            self.xmpp.users.remove(usr[0])
        self.xmpp.notify('on_presence_unavailable', msg)

    def on_message(self, msg):
        if msg['subject'] == 'list_users':
            return self.on_list_users(msg)
        if msg['subject'] == 'answer_full':
            return self.on_answer_full(msg)
        if msg['subject'] == 'chat':
            return self.xmpp.notify('on_msg', msg)
        if msg['subject'] == 'invite':
            return self.xmpp.notify('on_invite_chat', msg)

    def on_groupchat_message(self, msg):
        if msg['mucnick'] != self.xmpp.xmpp.boundjid.bare:
            return self.xmpp.notify('on_groupchat_msg', msg)

    def on_list_users(self, msg):
        self.xmpp.users = []
        self.xmpp.users = [User(line[1:], int(line[0]), True, self.xmpp) for line in msg['body'].split()]
        roster_users = [name for name in self.xmpp.xmpp.client_roster.keys() if self.xmpp.xmpp.client_roster[name] in ['to', 'both']]
        for user in ['ya2_yorg@jabb3r.org', self.boundjid.bare]:
            if user in roster_users: roster_users.remove(user)
        out_users = [usr for usr in roster_users if usr not in [_usr.name for _usr in self.xmpp.users]]
        self.xmpp.users += [User(usr, 0, False, self.xmpp) for usr in out_users]
        filter_names = ['ya2_yorg@jabb3r.org', self.boundjid.bare]
        presence_users = [usr.name_full for usr in self.xmpp.users if usr.name not in filter_names]
        for usr in presence_users:
            if usr not in self.presences_sent:
                self.xmpp.xmpp.send_presence(
                    pfrom=self.xmpp.xmpp.boundjid.full,
                    pto=usr)

        self.sort_users()
        self.xmpp.notify('on_users')

    def sort_users(self):
        sortusr = lambda usr: (usr.name == self.boundjid.bare, not usr.is_in_yorg, not usr.is_friend, not usr.is_supporter, usr.name)
        self.xmpp.users = sorted(self.xmpp.users, key=sortusr)

    def send_connected(self):
        self.send_presence(
            pfrom=self.boundjid.full,
            pto='ya2_yorg@jabb3r.org')
        self.send_message(
            mfrom=self.boundjid.full,
            mto='ya2_yorg@jabb3r.org',
            mtype='chat',
            msubject='query_full',
            mbody='query_full')

    def on_answer_full(self, msg):
        self.send_presence(
            pfrom=self.boundjid.full,
            pto=msg['from'])
        self.send_message(
            mfrom=self.boundjid.full,
            mto='ya2_yorg@jabb3r.org',
            mtype='chat',
            msubject='list_users',
            mbody='list_users')

    def destroy(self):
        self.del_event_handler('session_start', self.session_start)
        self.del_event_handler('failed_auth', self.on_ko)
        self.del_event_handler('message', self.on_message)
