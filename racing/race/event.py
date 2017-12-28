from itertools import chain
from panda3d.core import Vec3
from direct.interval.LerpInterval import LerpPosInterval, LerpHprInterval
from direct.interval.IntervalGlobal import LerpFunc
from yyagl.gameobject import Event
from yyagl.racing.car.ai import CarAi
from yyagl.racing.weapon.rocket.rocket import Rocket, RocketNetwork
from yyagl.racing.weapon.rear_rocket.rear_rocket import RearRocket, RearRocketNetwork
from yyagl.racing.weapon.turbo.turbo import Turbo
from yyagl.racing.weapon.rotate_all.rotate_all import RotateAll
from yyagl.racing.weapon.mine.mine import Mine, MineNetwork


class NetMsgs(object):
    game_packet = 200
    player_info = 201
    end_race_player = 202
    end_race = 203


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
            self.mdt.logic.props.season_props.gameprops.menu_args,
            self.mdt.logic.props.keys)
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

    @staticmethod
    def _rotate_car(t, node, start_vec, end_vec):
        interp_vec = Vec3(
            start_vec[0] * (1 - t) + end_vec[0] * t,
            start_vec[1] * (1 - t) + end_vec[1] * t,
            start_vec[2] * (1 - t) + end_vec[2] * t)
        node.look_at(node.get_pos() + interp_vec)

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
        fwd = render.get_relative_vector(self.mdt.logic.player_car.gfx.nodepath.node, Vec3(0, 1, 0))
        velocity = self.mdt.logic.player_car.get_linear_velocity()
        self.server_info['server'] = (pos, fwd, velocity)
        for car in [_car for _car in self.mdt.logic.cars if _car.ai_cls == CarAi]:
            pos = car.get_pos()
            fwd = render.get_relative_vector(car.gfx.nodepath.node, Vec3(0, 1, 0))
            velocity = car.get_linear_velocity()
            self.server_info[car] = (pos, fwd, velocity)
        if globalClock.get_frame_time() - self.last_sent > self.eng.server.rate:
            for conn, addr in self.eng.server.connections:
                self.eng.server.send_udp(self.__prepare_game_packet(), addr)
            self.last_sent = globalClock.get_frame_time()

    def __prepare_game_packet(self):
        packet = [NetMsgs.game_packet]
        for car in [self.mdt.logic.player_car] + self.mdt.logic.cars:
            name = car.name
            pos = car.gfx.nodepath.get_pos()
            fwd = render.get_relative_vector(car.gfx.nodepath.node, Vec3(0, 1, 0))
            velocity = car.phys.vehicle.getChassis().get_linear_velocity()
            level = 0
            nodes = car.gfx.nodepath.get_children()
            if len(nodes):
                curr_chassis = nodes[0]
                if car.gfx.chassis_np_low.get_name() in curr_chassis.get_name():
                    level = 1
                if car.gfx.chassis_np_hi.get_name() in curr_chassis.get_name():
                    level = 2
            else:  # still loading cars
                level = 0
            wpn_pos = (0, 0, 0)
            wpn_fwd = (0, 0, 0)
            if car.logic.weapon or car.logic.fired_weapons:
                curr_wpn = car.logic.weapon
                if not curr_wpn: curr_wpn = car.logic.fired_weapons[0]
                wpn = {
                    Rocket: 'rocket', RocketNetwork: 'rocket', RearRocket: 'rearrocket', RearRocketNetwork: 'rearrocket',
                    Turbo: 'turbo', RotateAll: 'rotateall', Mine: 'mine', MineNetwork: 'mine'}[curr_wpn.__class__]
                if curr_wpn.logic.has_fired:
                    wpn_pos = curr_wpn.gfx.gfx_np.node.get_pos(render)
                    wpn_fwd = render.get_relative_vector(curr_wpn.gfx.gfx_np.node, Vec3(0, 1, 0))
            else:
                wpn = ''
            packet += chain([name], pos, fwd, velocity, [level], [wpn], wpn_pos, wpn_fwd)
        return packet

    def __process_player_info(self, data_lst, sender):
        from yyagl.racing.car.car import NetworkCar
        pos = (data_lst[1], data_lst[2], data_lst[3])
        fwd = (data_lst[4], data_lst[5], data_lst[6])
        velocity = (data_lst[7], data_lst[8], data_lst[9])
        level = data_lst[10]
        weapon = data_lst[11]
        wpn_pos = (data_lst[12], data_lst[13], data_lst[14])
        wpn_fwd = (data_lst[15], data_lst[16], data_lst[17])
        self.server_info[sender] = (pos, fwd, velocity, level, weapon)
        car_name = self.eng.car_mapping[data_lst[-1]]
        for car in [car for car in self.mdt.logic.cars if car.__class__ == NetworkCar]:
            if car_name in car.name:
                LerpPosInterval(car.gfx.nodepath.node, .2, pos).start()
                fwd_start = render.get_relative_vector(car.gfx.nodepath.node, Vec3(0, 1, 0))
                LerpFunc(self._rotate_car,
                         fromData=0,
                         toData=1,
                         duration=self.eng.server.rate,
                         extraArgs=[car.gfx.nodepath.node, fwd_start, fwd]).start()
                curr_level = 0
                curr_chassis = car.gfx.nodepath.get_children()[0]
                if car.gfx.chassis_np_low.get_name() in curr_chassis.get_name():
                    curr_level = 1
                if car.gfx.chassis_np_hi.get_name() in curr_chassis.get_name():
                    curr_level = 2
                if curr_level != level:
                    car.logic.set_damage(level)
                if weapon:
                    wpn = {
                        'rocket': RocketNetwork, 'rearrocket': RearRocketNetwork,
                        'turbo': Turbo, 'rotateall': RotateAll, 'mine': Mine, 'mine': MineNetwork}[weapon]
                    if car.logic.weapon.__class__ != wpn:
                        car.event.set_weapon(wpn)
                    car.logic.weapon.update_props(wpn_pos, wpn_fwd)
                else:
                    if car.logic.weapon:
                        if car.logic.weapon.__class__ == RotateAll:
                            car.logic.weapon.fire(True)
                            car.logic.weapon = None
                        else: car.event.unset_weapon()
                    wpn = None

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
        for i in range(1, len(data_lst) - 1, 18):
            car_name = data_lst[i]
            car_pos = (data_lst[i + 1], data_lst[i + 2], data_lst[i + 3])
            car_fwd = (data_lst[i + 4], data_lst[i + 5], data_lst[i + 6])
            car_vel = (data_lst[i + 7], data_lst[i + 8], data_lst[i + 9])
            car_level = data_lst[i + 10]
            car_weapon = data_lst[i + 11]
            car_wpn_pos = (data_lst[i + 12], data_lst[i + 13], data_lst[i + 14])
            car_wpn_fwd = (data_lst[i + 15], data_lst[i + 16], data_lst[i + 17])
            cars = self.mdt.logic.cars
            netcars = [car for car in cars if car.__class__ == NetworkCar]
            for car in netcars:
                if car_name in car.name:
                    LerpPosInterval(car.gfx.nodepath.node, self.eng.client.rate, car_pos).start()
                    fwd_start = render.get_relative_vector(car.gfx.nodepath.node, Vec3(0, 1, 0))
                    LerpFunc(self._rotate_car,
                         fromData=0,
                         toData=1,
                         duration=self.eng.client.rate,
                         extraArgs=[car.gfx.nodepath.node, fwd_start, car_fwd]).start()
                    curr_level = 0
                    curr_chassis = car.gfx.nodepath.get_children()[0]
                    if car.gfx.chassis_np_low.get_name() in curr_chassis.get_name():
                        curr_level = 1
                    if car.gfx.chassis_np_hi.get_name() in curr_chassis.get_name():
                        curr_level = 2
                    if curr_level != car_level:
                        car.logic.set_damage(car_level)
                    if car_weapon:
                        wpn = {
                            'rocket': RocketNetwork, 'rearrocket': RearRocketNetwork,
                            'turbo': Turbo, 'rotateall': RotateAll, 'mine': Mine, 'mine': MineNetwork}[car_weapon]
                        if car.logic.weapon.__class__ != wpn:
                            car.event.set_weapon(wpn)
                        car.logic.weapon.update_props(car_wpn_pos, car_wpn_fwd)
                    else:
                        if car.logic.weapon:
                            if car.logic.weapon.__class__ == RotateAll:
                                car.logic.weapon.fire(True)
                                car.logic.weapon = None
                            else: car.event.unset_weapon()

    def process_client(self, data_lst, sender):
        if data_lst[0] == NetMsgs.game_packet:
            self.__process_game_packet(data_lst)
        if data_lst[0] == NetMsgs.end_race:
            if self.mdt.fsm.get_current_or_next_state() != 'Results':
                # forward the actual ranking
                dct = {'kronos': 0, 'themis': 0, 'diones': 0, 'iapeto': 0,
                       'phoibe': 0, 'rea': 0, 'iperion': 0, 'teia': 0}
                self.mdt.fsm.demand('Results', dct)
