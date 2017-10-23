from itertools import chain
from direct.interval.LerpInterval import LerpPosInterval, LerpHprInterval
from yyagl.gameobject import Event
from yyagl.racing.car.ai import CarAi


class NetMsgs(object):
    game_packet = 0
    player_info = 1
    end_race_player = 2
    end_race = 3


class RaceEvent(Event):

    def __init__(self, mdt, menu_cls, keys):
        Event.__init__(self, mdt)
        self.menu_cls = menu_cls
        self.accept(keys.pause, self.eng.toggle_pause)
        self.last_sent = globalClock.get_frame_time()  # for networking
        self.ingame_menu = None

    def network_register(self):
        pass

    def fire_ingame_menu(self):
        self.ignore('escape-up')
        self.eng.show_cursor()
        self.ingame_menu = self.menu_cls(
            self.mdt.logic.props.season_props.gameprops.menu_args)
        self.ingame_menu.gui.attach(self.on_ingame_back)
        self.ingame_menu.gui.attach(self.on_ingame_exit)

    def on_ingame_back(self):
        self.ingame_menu.gui.detach(self.on_ingame_back)
        self.ingame_menu.gui.detach(self.on_ingame_exit)
        self.register_menu()
        self.eng.hide_cursor()
        self.ingame_menu.destroy()

    def on_ingame_exit(self):
        self.ingame_menu.gui.detach(self.on_ingame_back)
        self.ingame_menu.gui.detach(self.on_ingame_exit)
        if self.mdt.fsm.getCurrentOrNextState() != 'Results':
            self.mdt.logic.exit_play()
        self.ingame_menu.destroy()
        self.notify('on_ingame_exit_confirm')

    def register_menu(self):
        self.accept('escape-up', self.fire_ingame_menu)

    def on_wrong_way(self, way_str):
        if way_str:
            self.mdt.gui.way_txt.setText(way_str)
        elif not self.mdt.logic.player_car.logic.is_moving:
            respawn_key = self.mdt.logic.props.keys.respawn
            txt = _('press %s to respawn') % respawn_key
            self.mdt.gui.way_txt.setText(txt)
        else:
            self.mdt.gui.way_txt.setText('')

    def on_end_race(self):
        points = [10, 8, 6, 4, 3, 2, 1, 0]
        zipped = zip(self.mdt.logic.race_ranking(), points)
        race_ranking = {car: point for car, point in zipped}
        self.mdt.fsm.demand('Results', race_ranking)

    def destroy(self):
        map(self.ignore, ['escape-up', 'p-up'])
        Event.destroy(self)


class RaceEventServer(RaceEvent):

    def __init__(self, mdt, menu_cls, keys):
        RaceEvent.__init__(self, mdt, menu_cls, keys)
        self.server_info = {}
        self.eng.attach_obs(self.on_frame)

    def network_register(self):
        self.eng.server.register_cb(self.process_srv)

    def on_frame(self):
        if not hasattr(self.mdt.logic, 'player_car') or \
                not hasattr(self.mdt.logic.player_car, 'phys') or \
                any([not hasattr(car, 'phys') for car in self.mdt.logic.cars]):
            return  # still loading; attach when the race has started
        pos = self.mdt.logic.player_car.get_pos()
        hpr = self.mdt.logic.player_car.get_hpr()
        velocity = self.mdt.logic.player_car.get_linear_velocity()
        self.server_info['server'] = (pos, hpr, velocity)
        for car in [_car for _car in self.mdt.logic.cars if _car.ai_cls == CarAi]:
            pos = car.get_pos()
            hpr = car.get_hpr()
            velocity = car.get_linear_velocity()
            self.server_info[car] = (pos, hpr, velocity)
        if globalClock.get_frame_time() - self.last_sent > .2:
            self.eng.server.send(self.__prepare_game_packet())
            self.last_sent = globalClock.get_frame_time()

    def __prepare_game_packet(self):
        packet = [NetMsgs.game_packet]
        for car in [self.mdt.logic.player_car] + self.mdt.logic.cars:
            name = car.name
            pos = car.gfx.nodepath.get_pos()
            hpr = car.gfx.nodepath.get_hpr()
            velocity = car.phys.vehicle.getChassis().get_linear_velocity()
            packet += chain([name], pos, hpr, velocity)
        return packet

    def __process_player_info(self, data_lst, sender):
        from yyagl.racing.car.car import NetworkCar
        pos = (data_lst[1], data_lst[2], data_lst[3])
        hpr = (data_lst[4], data_lst[5], data_lst[6])
        velocity = (data_lst[7], data_lst[8], data_lst[9])
        self.server_info[sender] = (pos, hpr, velocity)
        car_name = self.eng.car_mapping[sender]
        for car in [car for car in self.mdt.logic.cars if car.__class__ == NetworkCar]:
            if car_name in car.name:
                LerpPosInterval(car.gfx.nodepath.node, .2, pos).start()
                LerpHprInterval(car.gfx.nodepath.node, .2, hpr).start()

    def process_srv(self, data_lst, sender):
        if data_lst[0] == NetMsgs.player_info:
            self.__process_player_info(data_lst, sender)
        if data_lst[0] == NetMsgs.end_race_player:
            self.eng.server.send([NetMsgs.end_race])
            dct = {'kronos': 0, 'themis': 0, 'diones': 0, 'iapeto': 0,
                   'phoibe': 0, 'rea': 0, 'iperion': 0, 'teia': 0}
            self.mdt.fsm.demand('Results', dct)
            # forward the actual ranking
            self.mdt.gui.results.show(dct)

    def destroy(self):
        self.eng.detach_obs(self.on_frame)
        RaceEvent.destroy(self)


class RaceEventClient(RaceEvent):

    def network_register(self):
        self.eng.client.register_cb(self.process_client)

    def __process_game_packet(self, data_lst):
        from yyagl.racing.car.car import NetworkCar
        for i in range(1, len(data_lst), 10):
            car_name = data_lst[i]
            car_pos = (data_lst[i + 1], data_lst[i + 2], data_lst[i + 3])
            car_hpr = (data_lst[i + 4], data_lst[i + 5], data_lst[i + 6])
            cars = self.mdt.logic.cars
            netcars = [car for car in cars if car.__class__ == NetworkCar]
            for car in netcars:
                if car_name in car.name:
                    LerpPosInterval(car.gfx.nodepath.node, .2, car_pos).start()
                    LerpHprInterval(car.gfx.nodepath.node, .2, car_hpr).start()

    def process_client(self, data_lst, sender):
        if data_lst[0] == NetMsgs.game_packet:
            self.__process_game_packet(data_lst)
        if data_lst[0] == NetMsgs.end_race:
            if self.mdt.fsm.get_current_or_next_state() != 'Results':
                # forward the actual ranking
                dct = {'kronos': 0, 'themis': 0, 'diones': 0, 'iapeto': 0,
                       'phoibe': 0, 'rea': 0, 'iperion': 0, 'teia': 0}
                self.mdt.fsm.demand('Results', dct)
