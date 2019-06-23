from itertools import chain
from panda3d.core import Vec3, LPoint3f, NodePath
from direct.interval.LerpInterval import LerpPosInterval, LerpHprInterval
from direct.interval.IntervalGlobal import LerpFunc
from yyagl.gameobject import EventColleague
from yyagl.racing.car.ai import CarAi
from yyagl.racing.weapon.rocket.rocket import Rocket, RocketNetwork
from yyagl.racing.weapon.rear_rocket.rear_rocket import RearRocket, RearRocketNetwork
from yyagl.racing.weapon.turbo.turbo import Turbo, TurboNetwork
from yyagl.racing.weapon.rotate_all.rotate_all import RotateAll
from yyagl.racing.weapon.mine.mine import Mine, MineNetwork


class NetMsgs(object):
    game_packet = 200
    player_info = 201
    end_race_player = 202
    end_race = 203


wpnclasses2id = {
    Rocket: 1,
    RocketNetwork: 1,
    RearRocket: 2,
    RearRocketNetwork: 2,
    Turbo: 3,
    TurboNetwork: 3,
    RotateAll: 4,
    Mine: 5,
    MineNetwork: 5}


id2wpnclasses = {
    1: RocketNetwork,
    2: RearRocketNetwork,
    3: TurboNetwork,
    4: RotateAll,
    5: MineNetwork}


carname2id = {
    'themis': 1,
    'kronos': 2,
    'diones': 3,
    'iapeto': 4,
    'phoibe': 5,
    'rea': 6,
    'iperion': 7,
    'teia': 8}


id2carname = {
    1: 'themis',
    2: 'kronos',
    3: 'diones',
    4: 'iapeto',
    5: 'phoibe',
    6: 'rea',
    7: 'iperion',
    8: 'teia'}


class RaceEvent(EventColleague):

    def __init__(self, mediator, menu_cls, keys):
        EventColleague.__init__(self, mediator)
        self.menu_cls = menu_cls
        self.ended_cars = []
        self.__keys = keys
        if self.mediator.logic.props.season_props.kind in ['single', 'season']:
            self.accept(keys.pause, self.eng.toggle_pause)
        self.last_sent = self.eng.curr_time  # for networking
        self.ingame_menu = None

    def network_register(self):
        pass

    def fire_ingame_menu(self):
        self.ignore('escape-up')
        self.eng.show_cursor()
        self.ingame_menu = self.menu_cls(
            self.mediator.logic.props.season_props.gameprops.menu_props,
            self.mediator.logic.props.keys)
        self.ingame_menu.gui.attach(self.on_ingame_back)
        self.ingame_menu.gui.attach(self.on_ingame_exit)

    def on_ingame_back(self):
        self.ingame_menu.gui.detach(self.on_ingame_back)
        self.ingame_menu.gui.detach(self.on_ingame_exit)
        self.register_menu()
        self.eng.hide_cursor()
        self.ingame_menu = self.ingame_menu.destroy()

    def on_ingame_exit(self):
        self.ingame_menu.gui.detach(self.on_ingame_back)
        self.ingame_menu.gui.detach(self.on_ingame_exit)
        #if self.mediator.fsm.getCurrentOrNextState() != 'Results':
        #    self.mediator.logic.exit_play()
        self.ingame_menu = self.ingame_menu.destroy()
        self.notify('on_ingame_exit_confirm')

    def register_menu(self):
        self.accept('escape-up', self.fire_ingame_menu)

    def on_end_race(self, player_name):
        self.ended_cars += [player_name]
        if not all(pcar in self.ended_cars for pcar in self.mediator.logic.props.season_props.player_car_names): return
        points = [10, 8, 6, 4, 3, 2, 1, 0]
        zipped = zip(self.mediator.logic.race_ranking(), points)
        race_ranking = {car: point for car, point in zipped}
        if self.mediator.fsm.getCurrentOrNextState() != 'Results':
            self.mediator.fsm.demand('Results', race_ranking)

    def _move_car(self, car):
        if not hasattr(car, 'logic'): return  # it's created in the second frame
        t = self.eng.curr_time - car.logic.last_network_packet
        t = t / RaceEvent.eng.server.rate
        node = car.gfx.nodepath.node
        start_pos = car.logic.curr_network_start_pos
        end_pos = car.logic.curr_network_end_pos
        interp_pos = Vec3(
            start_pos[0] * (1 - t) + end_pos[0] * t,
            start_pos[1] * (1 - t) + end_pos[1] * t,
            start_pos[2] * (1 - t) + end_pos[2] * t)
        if t <= 1.0 and self.mediator.logic.min_dist(car) > 5:
            node.set_pos(interp_pos)

    def _rotate_car(self, car):
        if not hasattr(car, 'logic'): return  # it's created in the second frame
        t = self.eng.curr_time - car.logic.last_network_packet
        t = t / RaceEvent.eng.server.rate
        node = car.gfx.nodepath.node
        start_vec = car.logic.curr_network_start_vec
        end_vec = car.logic.curr_network_end_vec
        interp_vec = Vec3(
            float(start_vec[0]) * (1 - t) + float(end_vec[0]) * t,
            float(start_vec[1]) * (1 - t) + float(end_vec[1]) * t,
            float(start_vec[2]) * (1 - t) + float(end_vec[2]) * t)
        if t <= 1.0 and self.mediator.logic.min_dist(car) > 5:
            node.look_at(node.get_pos() + interp_vec)

    def destroy(self):
        list(map(self.ignore, ['escape-up', self.__keys.pause]))
        EventColleague.destroy(self)


class RaceEventServer(RaceEvent):

    def __init__(self, mediator, menu_cls, keys):
        RaceEvent.__init__(self, mediator, menu_cls, keys)
        self.server_info = {}
        self.eng.attach_obs(self.on_frame)
        self.players_ended = []
        self.end_race_sent = False

    def network_register(self):
        #self.eng.server.register_cb(self.process_srv)
        self.eng.client.attach(self.on_player_info)
        self.eng.client.attach(self.on_end_race_player)

    def on_frame(self):
        if not self.mediator.logic.player_cars or \
                not hasattr(self.mediator.logic.player_cars[0], 'phys') or \
                self.mediator.logic.cars is None or \
                any([not hasattr(car, 'phys') for car in self.mediator.logic.cars]):
            return  # still loading; attach when the race has started
        pos = self.mediator.logic.player_cars[0].get_pos()
        fwd = render.get_relative_vector(self.mediator.logic.player_cars[0].gfx.nodepath.node, Vec3(0, 1, 0))
        velocity = self.mediator.logic.player_cars[0].get_linear_velocity()
        self.server_info['server'] = (pos, fwd, velocity)
        from yyagl.racing.car.car import NetworkCar
        for car in [car for car in self.mediator.logic.cars if car.__class__ == NetworkCar]:
            self._move_car(car)
            self._rotate_car(car)
        for car in [_car for _car in self.mediator.logic.cars if _car.ai_cls == CarAi]:
            pos = car.get_pos()
            fwd = render.get_relative_vector(car.gfx.nodepath.node, Vec3(0, 1, 0))
            velocity = car.get_linear_velocity()
            self.server_info[car] = (pos, fwd, velocity)
        if self.eng.curr_time - self.last_sent > self.eng.server.rate:
            #for conn in self.eng.server.connections:
            self.eng.client.send_udp(self.__prepare_game_packet(), self.eng.client.myid)
            self.last_sent = self.eng.curr_time
        self.check_end()

    def __prepare_game_packet(self):
        packet = ['game_packet', self.eng.client.myid]
        for car in self.mediator.logic.player_cars + self.mediator.logic.cars:
            name = carname2id[car.name]
            pos = car.gfx.nodepath.get_pos()
            fwd = render.get_relative_vector(car.gfx.nodepath.node, Vec3(0, 1, 0))
            velocity = car.phys.vehicle.getChassis().get_linear_velocity()
            ang_vel = car.phys.vehicle.get_chassis().get_angular_velocity()
            try: curr_inp = car.event._get_input()
            except AttributeError as e:
                print(e)
                # car.event is created in the second frame
                from yyagl.racing.car.event import DirKeys
                curr_inp = DirKeys(False, False, False, False)
            inp = [curr_inp.forward, curr_inp.rear, curr_inp.left, curr_inp.right]
            eng_frc = car.phys.vehicle.get_wheel(0).get_engine_force()
            brk_frc_fwd = car.phys.vehicle.get_wheel(0).get_brake()
            brk_frc_rear = car.phys.vehicle.get_wheel(2).get_brake()
            steering = car.phys.vehicle.get_steering_value(0)
            level = 0
            nodes = car.gfx.nodepath.node.get_children()
            if len(nodes):
                curr_chassis = nodes[0]
                if car.gfx.chassis_np_low.name in curr_chassis.get_name():
                    level = 1
                if car.gfx.chassis_np_hi.name in curr_chassis.get_name():
                    level = 2
            else:  # still loading cars
                level = 0
            wpn = ''
            wpn_id = 0
            wpn_pos = (0, 0, 0)
            wpn_fwd = (0, 0, 0)
            if car.logic.weapon:
                curr_wpn = car.logic.weapon
                wpn_id = curr_wpn.id
                wpn = wpnclasses2id[curr_wpn.__class__]
                if curr_wpn.logic.has_fired:
                    wpn_pos = curr_wpn.gfx.gfx_np.node.get_pos(render)
                    wpn_fwd = render.get_relative_vector(curr_wpn.gfx.gfx_np.node, Vec3(0, 1, 0))
            packet += chain(
                [name], pos, fwd, velocity, ang_vel, inp,
                [eng_frc, brk_frc_fwd, brk_frc_rear, steering], [level],
                [wpn, wpn_id], wpn_pos, wpn_fwd)
            packet += [len(car.logic.fired_weapons)]
            for i in range(len(car.logic.fired_weapons)):
                curr_wpn = car.logic.fired_weapons[i]
                wpn = wpnclasses2id[curr_wpn.__class__]
                wpn_pos = curr_wpn.gfx.gfx_np.node.get_pos(render)
                wpn_fwd = render.get_relative_vector(curr_wpn.gfx.gfx_np.node, Vec3(0, 1, 0))
                packet += chain([wpn, curr_wpn.id], wpn_pos, wpn_fwd)
        return packet

    def on_player_info(self, data_lst):
        from yyagl.racing.car.car import NetworkCar
        sender = data_lst[0]
        pos = (data_lst[1], data_lst[2], data_lst[3])
        fwd = (data_lst[4], data_lst[5], data_lst[6])
        velocity = (data_lst[7], data_lst[8], data_lst[9])
        ang_vel = (data_lst[10], data_lst[11], data_lst[12])
        curr_inp = (data_lst[13], data_lst[14], data_lst[15], data_lst[16])
        eng_frc = data_lst[17]
        brk_frc_fwd = data_lst[18]
        brk_frc_rear = data_lst[19]
        steering = data_lst[20]
        level = data_lst[21]
        weapon, car_wpn_id = data_lst[22], data_lst[23]
        wpn_pos = (data_lst[24], data_lst[25], data_lst[26])
        wpn_fwd = (data_lst[27], data_lst[28], data_lst[29])
        fired_weapons = []
        for i in range(data_lst[30]):
            start = 31 + i * 8
            fired_weapons += [[
                data_lst[start],
                data_lst[start + 1],
                (data_lst[start + 2], data_lst[start + 3], data_lst[start + 4]),
                (data_lst[start + 5], data_lst[start + 6], data_lst[start + 7])
            ]]
        self.server_info[sender] = (pos, fwd, velocity, ang_vel, curr_inp, level, weapon)
        car_name = self.eng.car_mapping[sender]
        if not self.mediator:
            print("received player_info packet while we've quit")
            return
        for car in [car for car in self.mediator.logic.cars if car.__class__ == NetworkCar]:
            if carname2id[car_name] == carname2id[car.name]:
                car.logic.last_network_packet = self.eng.curr_time
                car.logic.curr_network_start_pos = car.gfx.nodepath.get_pos()
                car.logic.curr_network_end_pos = pos
                car.logic.curr_network_start_vec = render.get_relative_vector(car.gfx.nodepath.node, Vec3(0, 1, 0))
                car.logic.curr_network_end_vec = fwd
                car.logic.curr_network_eng_frc = eng_frc
                car.logic.curr_network_brk_frc_fwd = brk_frc_fwd
                car.logic.curr_network_brk_frc_rear = brk_frc_rear
                car.logic.curr_network_steering = steering
                from yyagl.racing.car.event import DirKeys
                car.logic.curr_network_input = DirKeys(*curr_inp)
                curr_level = 0
                curr_chassis = car.gfx.nodepath.node.get_children()[0]
                if car.gfx.chassis_np_low.node.get_name() in curr_chassis.get_name():
                    curr_level = 1
                if car.gfx.chassis_np_hi.node.get_name() in curr_chassis.get_name():
                    curr_level = 2
                if curr_level != level:
                    car.logic.set_damage(level)
                for wpn_chunk in fired_weapons:
                    wpn_code, wpn_id, wpn_pos, wpn_fwd = wpn_chunk
                    wpn = id2wpnclasses[wpn_code]
                    curr_wpn = self.__lookup_wpn(car, wpn, wpn_id, wpn_pos, wpn_fwd)
                    if not curr_wpn:
                        if car.logic.weapon:
                            car.event.set_fired_weapon()
                    else:
                        curr_wpn.update_fired_props(wpn_pos, wpn_fwd)
                self.__clean_fired_weapons(car, fired_weapons)
                if weapon:
                    wpn = id2wpnclasses[weapon]
                    if car.logic.weapon.__class__ != wpn:
                        car.event.set_weapon(wpn, car_wpn_id)
                    car.logic.weapon.update_props(wpn_pos, wpn_fwd)
                else:
                    if car.logic.weapon:
                        if car.logic.weapon.__class__ == RotateAll:
                            car.logic.weapon.fire(True)
                            car.logic.weapon = None
                        else: car.event.unset_weapon()
                    wpn = None

    def __lookup_wpn(self, car, wpn, wpn_id, wpn_pos, wpn_fwd):
        wpns = [_wpn for _wpn in car.logic.fired_weapons if _wpn.id == wpn_id]
        if wpns: return wpns[0]

    def __clean_fired_weapons(self, car, fired_weapons):
        found_wpn = []
        for wpn_chunk in fired_weapons:
            wpn_code, wpn_id, wpn_pos, wpn_fwd = wpn_chunk
            wpn = id2wpnclasses[wpn_code]
            found_wpn += [self.__lookup_wpn(car, wpn, wpn_id, wpn_pos, wpn_fwd)]
        notfound_wpn = [wpn for wpn in car.logic.fired_weapons if wpn not in found_wpn]
        for wpn in notfound_wpn:
            car.event.unset_fired_weapon(wpn)

    def on_end_race(self, player_name):
        self.ended_cars += [player_name]
        points = [10, 8, 6, 4, 3, 2, 1, 0]
        zipped = zip(self.mediator.logic.race_ranking(), points)
        race_ranking = {car: point for car, point in zipped}
        if self.mediator.fsm.getCurrentOrNextState() != 'Results':
            self.mediator.fsm.demand('Results', race_ranking)

    def on_end_race_player(self, uid):
        self.players_ended += [uid]

    def check_end(self):
        if self.end_race_sent: return
        if not self.mediator.gui.results.result_frm: return
        connections = [conn[0] for conn in self.eng.server.connections]
        if not all(conn in self.players_ended for conn in connections): return
        self.end_race_sent = True
        self.eng.client.send(['end_race'])
        self.mediator.gui.results.show_continue_btn()

    def destroy(self):
        self.eng.detach_obs(self.on_frame)
        self.eng.client.detach(self.on_player_info)
        RaceEvent.destroy(self)


class RaceEventClient(RaceEvent):

    def __init__(self, mediator, menu_cls, keys):
        RaceEvent.__init__(self, mediator, menu_cls, keys)
        self.eng.attach_obs(self.on_frame)
        #self.eng.xmpp.attach(self.on_server_quit)

    def on_frame(self):
        from yyagl.racing.car.car import NetworkCar
        if not self.mediator.logic.cars: return  # during loading
        for car in [car for car in self.mediator.logic.cars if car.__class__ == NetworkCar]:
            self._move_car(car)
            self._rotate_car(car)

    def network_register(self):
        #self.eng.client.register_cb(self.process_client)
        self.eng.client.attach(self.on_game_packet)
        self.eng.client.attach(self.on_end_race)

    def on_server_quit(self):
        if self.ingame_menu: self.on_ingame_back()
        self.ignore('escape-up')

    def on_game_packet(self, data_lst):
        from yyagl.racing.car.car import NetworkCar
        data_lst = data_lst[1:]
        while len(data_lst) > 1:
            car_name = id2carname[data_lst[0]]
            car_pos = (data_lst[1], data_lst[2], data_lst[3])
            car_fwd = (data_lst[4], data_lst[5], data_lst[6])
            car_vel = (data_lst[7], data_lst[8], data_lst[9])
            car_ang_vel = (data_lst[10], data_lst[11], data_lst[12])
            car_inp = (data_lst[13], data_lst[14], data_lst[15], data_lst[16])
            eng_frc = data_lst[17]
            brk_frc_fwd = data_lst[18]
            brk_frc_rear = data_lst[19]
            steering = data_lst[20]
            car_level = data_lst[21]
            car_weapon, car_wpn_id = data_lst[22], data_lst[23]
            car_wpn_pos = (data_lst[24], data_lst[25], data_lst[26])
            car_wpn_fwd = (data_lst[27], data_lst[28], data_lst[29])
            fired_weapons = []
            for i in range(data_lst[30]):
                start = 31 + i * 8
                fired_weapons += [[
                    data_lst[start], data_lst[start + 1],
                    (data_lst[start + 2], data_lst[start + 3], data_lst[start + 4]),
                    (data_lst[start + 5], data_lst[start + 6], data_lst[start + 7])
                ]]
            data_lst = data_lst[31 + data_lst[30] * 8:]
            cars = self.mediator.logic.cars
            netcars = [car for car in cars if car.__class__ == NetworkCar]
            for car in netcars:
                if car_name == car.name:
                    car.logic.last_network_packet = self.eng.curr_time
                    car.logic.curr_network_start_pos = car.gfx.nodepath.get_pos()
                    car.logic.curr_network_end_pos = car_pos
                    car.logic.curr_network_start_vec = render.get_relative_vector(car.gfx.nodepath.node, Vec3(0, 1, 0))
                    car.logic.curr_network_end_vec = car_fwd
                    car.logic.curr_network_eng_frc = eng_frc
                    car.logic.curr_network_brk_frc_fwd = brk_frc_fwd
                    car.logic.curr_network_brk_frc_rear = brk_frc_rear
                    car.logic.curr_network_steering = steering
                    from yyagl.racing.car.event import DirKeys
                    car.logic.curr_network_input = DirKeys(*car_inp)
                    curr_level = 0
                    curr_chassis = car.gfx.nodepath.node.get_children()[0]
                    if car.gfx.chassis_np_low.name in curr_chassis.get_name():
                        curr_level = 1
                    if car.gfx.chassis_np_hi.name in curr_chassis.get_name():
                        curr_level = 2
                    if curr_level != car_level:
                        car.logic.set_damage(car_level)
                    for wpn_chunk in fired_weapons:
                        wpn_code, wpn_id, wpn_pos, wpn_fwd = wpn_chunk
                        wpn = id2wpnclasses[wpn_code]
                        curr_wpn = self.__lookup_wpn(car, wpn, wpn_id, wpn_pos, wpn_fwd)
                        if not curr_wpn:
                            if car.logic.weapon:
                                car.event.set_fired_weapon()
                        else:
                            curr_wpn.update_fired_props(wpn_pos, wpn_fwd)
                    self.__clean_fired_weapons(car, fired_weapons)
                    if car_weapon:
                        wpn = id2wpnclasses[car_weapon]
                        if car.logic.weapon.__class__ != wpn:
                            car.event.set_weapon(wpn, car_wpn_id)
                        car.logic.weapon.update_props(car_wpn_pos, car_wpn_fwd)
                    else:
                        if car.logic.weapon:
                            if car.logic.weapon.__class__ == RotateAll:
                                car.logic.weapon.fire(True)
                                car.logic.weapon = None
                            else: car.event.unset_weapon()

    def __lookup_wpn(self, car, wpn, wpn_id, wpn_pos, wpn_fwd):
        wpns = [_wpn for _wpn in car.logic.fired_weapons if _wpn.id == wpn_id]
        if wpns: return wpns[0]

    def __clean_fired_weapons(self, car, fired_weapons):
        found_wpn = []
        for wpn_chunk in fired_weapons:
            wpn_code, wpn_id, wpn_pos, wpn_fwd = wpn_chunk
            wpn = id2wpnclasses[wpn_code]
            found_wpn += [self.__lookup_wpn(car, wpn, wpn_id, wpn_pos, wpn_fwd)]
        notfound_wpn = [wpn for wpn in car.logic.fired_weapons if wpn not in found_wpn]
        for wpn in notfound_wpn:
            car.event.unset_fired_weapon(wpn)

    def process_client(self, data_lst, sender):
        if data_lst[0] == NetMsgs.game_packet:
            self.__process_game_packet(data_lst)

    def on_end_race(self, uid):
        if self.mediator.fsm.getCurrentOrNextState() != 'Results':
            points = [10, 8, 6, 4, 3, 2, 1, 0]
            zipped = zip(self.mediator.logic.race_ranking(), points)
            race_ranking = {car: point for car, point in zipped}
            self.mediator.fsm.demand('Results', race_ranking)

    def destroy(self):
        self.eng.client.detach(self.on_game_packet)
        self.eng.detach_obs(self.on_frame)
        #self.eng.xmpp.detach(self.on_server_quit)
        RaceEvent.destroy(self)
