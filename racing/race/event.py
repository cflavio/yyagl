from itertools import chain
from direct.interval.LerpInterval import LerpPosInterval, LerpHprInterval
from yyagl.engine.network.server import Server
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
        self.accept(keys['pause'], eng.toggle_pause)
        self.last_sent = globalClock.getFrameTime()  # for networking
        self.ingame_menu = None

    def network_register(self):
        pass

    def fire_menu(self):
        self.ignore('escape-up')
        eng.show_cursor()
        self.ingame_menu = self.menu_cls()
        self.ingame_menu.gui.menu.attach_obs(self.on_ingame_back)
        self.ingame_menu.gui.menu.attach_obs(self.on_ingame_exit)

    def on_ingame_back(self):
        self.ingame_menu.gui.menu.detach_obs(self.on_ingame_back)
        self.ingame_menu.gui.menu.detach_obs(self.on_ingame_exit)
        self.register_menu()
        eng.hide_cursor()
        self.ingame_menu.destroy()

    def on_ingame_exit(self):
        self.ingame_menu.gui.menu.detach_obs(self.on_ingame_back)
        self.ingame_menu.gui.menu.detach_obs(self.on_ingame_exit)
        if self.mdt.fsm.getCurrentOrNextState() != 'Results':
            self.mdt.logic.exit_play()
        self.ingame_menu.destroy()
        self.notify('on_ingame_exit_confirm')

    def register_menu(self):
        self.accept('escape-up', self.fire_menu)

    def on_wrong_way(self, way_str):
        self.mdt.gui.way_txt.setText(way_str)

    def on_respawn(self, is_moving):
        respawn_key = self.mdt.logic.props.keys['respawn']
        txt = '' if is_moving else _('press %s to respawn') % respawn_key
        self.mdt.gui.way_txt.setText(txt)

    def on_end_race(self):
        points = [10, 8, 6, 4, 3, 2, 1, 0]
        zipped = zip(self.mdt.logic.race_ranking(), points)
        race_ranking = {car: point for car, point in zipped}
        self.mdt.fsm.demand('Results', race_ranking)

    def destroy(self):
        self.ignore('escape-up')
        self.ignore('p-up')
        Event.destroy(self)


class RaceEventServer(RaceEvent):

    def __init__(self, mdt):
        RaceEvent.__init__(self, mdt)
        self.server_info = {}
        eng.attach_obs(self.on_frame)

    def network_register(self):
        eng.register_server_cb(self.process_srv)

    def on_frame(self):
        if not hasattr(self.mdt.logic, 'player_car') or \
                not hasattr(self.mdt.logic.player_car, 'phys') or \
                any([not hasattr(car, 'phys') for car in game.cars]):
            return  # still loading; attach when the race has started
        pos = self.mdt.logic.player_car.getPos()
        hpr = self.mdt.logic.player_car.getHpr()
        velocity = self.mdt.logic.player_car.getLinearVelocity()
        self.server_info['server'] = (pos, hpr, velocity)
        for car in [car for car in game.cars if car.ai_cls == CarAi]:
            pos = car.get_pos()
            hpr = car.get_hpr()
            velocity = car.getLinearVelocity()
            self.server_info[car] = (pos, hpr, velocity)
        if globalClock.getFrameTime() - self.last_sent > .2:
            Server().send(self.__prepare_game_packet())
            self.last_sent = globalClock.getFrameTime()

    @staticmethod
    def __prepare_game_packet():
        packet = [NetMsgs.game_packet]
        for car in [game.player_car] + game.cars:
            name = car.gfx.path
            pos = car.gfx.nodepath.getPos()
            hpr = car.gfx.nodepath.getHpr()
            velocity = car.phys.vehicle.getChassis().getLinearVelocity()
            packet += chain([name], pos, hpr, velocity)
        return packet

    def __process_player_info(self, data_lst, sender):
        from racing.car.car import NetworkCar
        pos = (data_lst[1], data_lst[2], data_lst[3])
        hpr = (data_lst[4], data_lst[5], data_lst[6])
        velocity = (data_lst[7], data_lst[8], data_lst[9])
        self.server_info[sender] = (pos, hpr, velocity)
        car_name = eng.car_mapping[sender]
        for car in [car for car in game.cars if car.__class__ == NetworkCar]:
            if car_name in car.path:
                LerpPosInterval(car.gfx.nodepath, .2, pos).start()
                LerpHprInterval(car.gfx.nodepath, .2, hpr).start()

    def process_srv(self, data_lst, sender):
        if data_lst[0] == NetMsgs.player_info:
            self.__process_player_info(data_lst, sender)
        if data_lst[0] == NetMsgs.end_race_player:
            Server().send([NetMsgs.end_race])
            dct = {'kronos': 0, 'themis': 0, 'diones': 0, 'iapeto': 0,
                   'phoibe': 0, 'rea': 0, 'iperion': 0}
            self.mdt.fsm.demand('Results', dct)
            # forward the actual ranking
            self.mdt.gui.results.show(dct)

    def destroy(self):
        eng.detach_obs(self.on_frame)
        RaceEvent.destroy(self)


class RaceEventClient(RaceEvent):

    def network_register(self):
        eng.register_client_cb(self.process_client)

    @staticmethod
    def __process_game_packet(data_lst):
        from racing.car.car import NetworkCar
        for i in range(1, len(data_lst), 10):
            car_name = data_lst[i]
            car_pos = (data_lst[i + 1], data_lst[i + 2], data_lst[i + 3])
            car_hpr = (data_lst[i + 4], data_lst[i + 5], data_lst[i + 6])
            # cars = self.mdt.logic.cars
            # netcars = [car for car in cars if car.__class__ == NetworkCar]
            # for car in netcars:
            #     if car_name in car.path:
            #         LerpPosInterval(car.gfx.nodepath, .2, car_pos).start()
            #         LerpHprInterval(car.gfx.nodepath, .2, car_hpr).start()

    def process_client(self, data_lst, sender):
        if data_lst[0] == NetMsgs.game_packet:
            self.__process_game_packet(data_lst)
        if data_lst[0] == NetMsgs.end_race:
            if self.mdt.fsm.getCurrentOrNextState() != 'Results':
                # forward the actual ranking
                dct = {'kronos': 0, 'themis': 0, 'diones': 0, 'iapeto': 0,
                       'phoibe': 0, 'rea': 0, 'iperion': 0}
                self.mdt.fsm.demand('Results', dct)
