import logging
from yyagl.observer import Subject
from yyagl.gameobject import GameObject


try:
    from sleekxmpp import ClientXMPP
    from sleekxmpp.jid import JID
except ImportError:  # sleekxmpp requires openssl 1.0.2
    print 'OpenSSL 1.0.2 not detected'

    class ClientXMPP(object):

        def __init__(self, jid, password):
            taskMgr.doMethodLater(.5, lambda tsk: self.on_ok(), 'on ok')

        def add_event_handler(self, msg, callback): pass

        def register_plugin(self, plugin): pass

        def connect(self): pass

        def send_presence(self, pfrom, pto): pass

        def send_message(self, mfrom, mto, mtype, mbody): pass

        def disconnect(self): pass


class User(object):

    def __init__(self, name_full, is_supporter, is_in_yorg, is_playing, xmpp,
                 is_online=False):
        self.name_full = name_full
        self.name = JID(name_full).bare
        self.is_supporter = is_supporter
        self.is_in_yorg = is_in_yorg
        self.is_playing = is_playing
        self.is_online = is_online
        self.xmpp = xmpp
        self.public_addr = ''
        self.local_addr = ''

    @property
    def is_friend(self):
        return self.name in self.xmpp.friends


class XMPP(GameObject, Subject):

    def __init__(self, yorg_srv):
        Subject.__init__(self)
        GameObject.__init__(self)
        self.client = None
        self.yorg_srv = yorg_srv
        self.is_server_up = False
        self.users = []

    def start(self, usr, pwd, on_ok, on_fail, debug=False):
        logging.basicConfig(level=logging.DEBUG if debug else logging.INFO,
                            format='%(levelname)-8s %(message)s')
        self.client = YorgClient(usr, pwd, on_ok, on_fail, self)
        self.client.register_plugin('xep_0030')  # Service Discovery
        self.client.register_plugin('xep_0004')  # Data Forms
        self.client.register_plugin('xep_0060')  # PubSub
        self.client.register_plugin('xep_0199')  # XMPP Ping
        self.client.register_plugin('xep_0045')  # Multi-User Chat
        # self.client.register_plugin('xep_0059')
        if self.client.connect(): self.client.process()

    def send_connected(self):
        self.client.send_connected()

    def disconnect(self):
        if self.client:
            self.client.disconnect()
            self.client = self.client.destroy()

    @property
    def users_nodup(self):  # todo: once a frame
        users = []
        for usr in self.users:
            if any(_usr.name == usr.name for _usr in users): continue
            if usr.is_in_yorg: users += [usr]
            elif not any(_usr.name == usr.name for _usr in users):
                other_in_yorg = False
                others = [_usr for _usr in self.users if _usr.name == usr.name]
                for _usr in others:
                    if _usr.is_in_yorg: other_in_yorg = True
                if not other_in_yorg: users += [usr]
        return users

    @property
    def friends(self):
        return self.client.friends

    def is_friend(self, name):
        return name in self.client.friends

    def find_usr(self, usr_name):
        users = [usr for usr in self.users if usr.name == usr_name]
        if users: return users[0]

    def destroy(self):
        self.disconnect()
        Subject.destroy(self)
        GameObject.destroy(self)


class YorgClient(ClientXMPP, GameObject):

    def __init__(self, jid, password, on_ok, on_ko, xmpp):
        GameObject.__init__(self)
        self.xmpp = xmpp
        self.presences_sent = []
        self.registered = []
        ClientXMPP.__init__(self, jid, password)
        self.on_ok = on_ok
        self.on_ko = on_ko
        events = [
            'session_start', 'failed_auth', 'message', 'groupchat_message',
            'presence_subscribe', 'presence_subscribed', 'presence_available',
            'presence_unavailable',
            # 'groupchat_invite'  # we may receive non-yorg invites
            ]
        for evt in events:
            self.add_event_handler(
                evt, lambda msg, _evt=evt: self.dispatch_msg(_evt, msg))

    def dispatch_msg(self, code, msg):
        code2cb = {
            'session_start': [self.session_start],
            'failed_auth': [self.on_ko, [msg]],
            'message': [self.on_message, [msg]],
            'groupchat_message': [self.on_groupchat_message, [msg]],
            'subscribe': [self.on_subscribe, [msg]],
            'subscribed': [self.on_subscribed],
            'presence_available': [self.on_presence_available, [msg]],
            'presence_unavailable': [self.on_presence_unavailable, [msg]]}
        for _code, cb_args in code2cb.items():
            args = cb_args[1] if len(cb_args) > 1 else []
            if code == _code: self.eng.cb_mux.add_cb(cb_args[0], args)

    def session_start(self):
        self.eng.log('session start')
        self.send_presence()
        self.get_roster()
        logging.info(self.client_roster)
        self.on_ok()
        res = self['xep_0030'].get_items(jid=self.xmpp.client.boundjid.server,
                                         iterator=True)
        for itm in res['disco_items']:
            if 'conference' in itm['jid']:
                self.xmpp.client.conf_srv = itm['jid']

    @property
    def friends(self):
        friends = [usr for usr in self.client_roster.keys()
                   if self.client_roster[usr]['subscription'] in ['both']]
        return friends

    def on_subscribe(self, msg):
        self.eng.log('on subscribe ' + str(msg['from']))
        if self.xmpp.is_friend(msg['from']): return
        self.xmpp.notify('on_user_subscribe', msg['from'])
        logging.info('subscribe ' + str(self.client_roster))
        self.xmpp.notify('on_users')

    def on_subscribed(self):
        self.eng.log('on subscribed')
        logging.info('subscribed ' + str(self.client_roster))
        self.xmpp.notify('on_users')

    def on_presence_available(self, msg):
        _from = str(msg['from'])
        res = JID(msg['from'].resource)
        room = str(JID(msg['muc']['room']).bare)
        nick = str(msg['muc']['nick'])
        is_user = nick == res.user + '@' + res.server
        args = (_from, res, room, nick, is_user)
        self.eng.log('presence available: %s, %s, %s, %s, %s' % args)
        if _from == room: return
        if _from == room + '/' + nick and is_user:
            self.xmpp.notify('on_presence_available_room', msg)
            return
        if str(msg['from'].bare) not in [usr.name for usr in self.xmpp.users]:
            new_usr = User(msg['from'], 0, False, False, self.xmpp, True)
            self.xmpp.users += [new_usr]
            # TODO: create with is_in_yorg == False and use a stanza for
            # setting is_in_yorg = True
        else:
            for usr in self.xmpp.users:
                if msg['from'].bare == usr.name and not usr.is_in_yorg:
                    usr.name_full = str(msg['from'])
                    usr.is_online = True
        self.sort_users()
        not_from_me = msg['from'].bare != self.xmpp.client.boundjid.bare
        if not_from_me and msg['from'] not in self.presences_sent:
            self.presences_sent += [msg['from']]
            self.eng.log('send presence to ' + str(msg['from']))
            self.xmpp.client.send_presence(
                pfrom=self.xmpp.client.boundjid.full,
                pto=msg['from'])
        self.xmpp.notify('on_presence_available', msg)

    def on_presence_unavailable(self, msg):
        _from = str(msg['from'])
        res = JID(msg['from'].resource)
        room = str(JID(msg['muc']['room']).bare)
        nick = str(msg['muc']['nick'])
        is_user = nick == res.user + '@' + res.server
        args = (_from, res, room, nick, is_user)
        self.eng.log('presence unavailable: %s, %s, %s, %s, %s' % args)
        if _from == room + '/' + nick and is_user:
            self.xmpp.notify('on_presence_unavailable_room', msg)
            return
        _usr = [usr for usr in self.xmpp.users if usr.name == msg['from'].bare]
        if _usr:  # we receive unavailable for nonlogged users at the beginning
            if _usr[0].name not in self.client_roster:
                self.xmpp.users.remove(_usr[0])
            else:
                for _usr in self.xmpp.users:
                    if _from == _usr.name_full:
                        _usr.is_online = False
                        _usr.is_in_yorg = False
        else:
            self.xmpp.users += [User(_from, 0, False, False, self.xmpp)]
        self.xmpp.notify('on_presence_unavailable', msg)

    def register(self, msg): self.registered += [msg]

    def unregister(self, msg): self.registered.remove(msg)

    def is_registered(self, msg): return msg in self.registered

    def on_message(self, msg):
        self.eng.log('message: ' + msg['subject'])
        if msg['type'] == 'error': return
        lab2cb = {
            'list_users': [self.on_list_users, msg],
            'answer_full': [self.on_answer_full, msg],
            'chat': [self.xmpp.notify, 'on_msg', msg],
            'invite': [self.xmpp.notify, 'on_invite_chat', msg],
            'declined': [self.xmpp.notify, 'on_declined', msg],
            'cancel_invite': [self.xmpp.notify, 'on_cancel_invite'],
            'ip_address': [self.xmpp.notify, 'on_ip_address', msg],
            'yorg_init': [self.xmpp.notify, 'on_yorg_init', msg],
            'is_playing': [self.xmpp.notify, 'on_is_playing', msg]}
        for lab, cb_args in lab2cb.items():
            if self.is_registered(lab) and msg['subject'] == lab:
                return cb_args[0](*cb_args[1:])

    def on_groupchat_message(self, msg):
        return self.xmpp.notify('on_groupchat_msg', msg)

    def on_list_users(self, msg):
        jid = self.boundjid
        self.unregister('list_users')
        out_users = self.xmpp.users[:]
        self.xmpp.users = [
            User(line[2:], int(line[0]), True, int(line[1]), self.xmpp, True)
            for line in msg['body'].split()]
        for usr in out_users:
            if usr.name not in [_usr.name for _usr in self.xmpp.users]:
                new_usr = User(usr.name_full, 0, False, False, self.xmpp,
                               usr.is_online)
                self.xmpp.users += [new_usr]
        filter_names = [self.xmpp.yorg_srv, jid.bare]
        presence_users = [usr.name_full for usr in self.xmpp.users
                          if usr.name not in filter_names and usr.is_in_yorg]
        me = [usr for usr in self.xmpp.users if usr.name == jid.bare][0]
        for usr in presence_users:
            if usr not in self.presences_sent:
                self.xmpp.client.send_presence(
                    pfrom=self.xmpp.client.boundjid.full,
                    pto=usr)
            self.send_message(
                mfrom=jid.full,
                mto=usr,
                mtype='ya2_yorg',
                msubject='yorg_init',
                mbody='1' if me.is_supporter else '0')
        self.sort_users()
        self.xmpp.notify('on_users')

    def sort_users(self):
        sortusr = lambda usr: (
            usr.name == self.boundjid.bare, not usr.is_in_yorg,
            not usr.is_friend, not usr.is_supporter, usr.name)
        self.xmpp.users = sorted(self.xmpp.users, key=sortusr)

    def send_connected(self):
        self.eng.log('send connected')
        self.send_presence(
            pfrom=self.boundjid.full,
            pto=self.xmpp.yorg_srv)
        self.register('answer_full')
        self.send_message(
            mfrom=self.boundjid.full,
            mto=self.xmpp.yorg_srv,
            mtype='chat',
            msubject='query_full',
            mbody='query_full')

    def on_answer_full(self, msg):
        self.eng.log('received answer full')
        self.unregister('answer_full')
        self.xmpp.is_server_up = True
        self.send_presence(
            pfrom=self.boundjid.full,
            pto=msg['from'])
        self.register('list_users')
        self.register('yorg_init')
        self.register('invite')
        self.register('declined')
        self.register('cancel_invite')
        self.register('ip_address')
        self.register('is_playing')
        self.register('chat')
        self.send_message(
            mfrom=self.boundjid.full,
            mto=self.xmpp.yorg_srv,
            mtype='chat',
            msubject='list_users',
            mbody='list_users')

    def destroy(self):
        self.eng.log('destroyed xmpp')
        self.del_event_handler('session_start', self.session_start)
        self.del_event_handler('failed_auth', self.on_ko)
        self.del_event_handler('message', self.on_message)
        GameObject.destroy(self)
