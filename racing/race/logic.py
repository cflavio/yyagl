from yyagl.gameobject import Logic
from yyagl.racing.track.track import Track
from yyagl.racing.car.car import Car, PlayerCar, PlayerCarServer, \
    PlayerCarClient, NetworkCar, AiCar


class NetMsgs(object):

    client_ready = 0
    start_race = 1


class RaceLogic(Logic):

    cars = ['kronos', 'themis', 'diones', 'iapeto']

    def __init__(
            self, mdt, keys, joystick, sounds, color_main, color, font,
            coll_path, coll_name, car_path, phys_file, wheel_names,
            tuning_engine, tuning_tires, tuning_suspensions, road_name,
            base_path, model_name, damage_paths, wheel_gfx_names,
            particle_path, drivers, shaders, music_path, coll_track_path,
            unmerged, merged, ghosts, corner_names, waypoint_names,
            show_waypoints, weapons, weapon_names, start, track_name,
            track_path, track_model_name, empty_name, anim_name, omni_tag,
            thanks, sign_name, camera_vec, shadow_src, laps):
        self.load_txt = None
        self.cam_tsk = None
        self.cam_node = None
        self.send_tsk = None
        self.cam_pivot = None
        self.ready_clients = None
        self.preview = None
        self.curr_load_txt = None
        self.keys = keys
        self.joystick = joystick
        self.sounds = sounds
        self.color_main = color_main
        self.color = color
        self.font = font
        self.car_path = car_path
        self.coll_path = coll_path
        self.coll_name = coll_name
        self.phys_file = phys_file
        self.wheel_names = wheel_names
        self.tuning_engine = tuning_engine
        self.tuning_tires = tuning_tires
        self.tuning_suspensions = tuning_suspensions
        self.road_name = road_name
        self.base_path = base_path
        self.model_name = model_name
        self.damage_paths = damage_paths
        self.wheel_gfx_names = wheel_gfx_names
        self.particle_path = particle_path
        self.drivers_dct = drivers
        self.shaders = shaders
        self.music_path = music_path
        self.coll_track_path = coll_track_path
        self.unmerged = unmerged
        self.merged = merged
        self.ghosts = ghosts
        self.corner_names = corner_names
        self.waypoint_names = waypoint_names
        self.show_waypoints = show_waypoints
        self.weapons = weapons
        self.weapon_names = weapon_names
        self.start_name = start
        self.track_name = track_name
        self.track_path = track_path
        self.track_model_name = track_model_name
        self.empty_name = empty_name
        self.anim_name = anim_name
        self.omni_tag = omni_tag
        self.thanks = thanks
        self.sign_name = sign_name
        self.camera_vec = camera_vec
        self.shadow_src = shadow_src
        self.laps = laps
        Logic.__init__(self, mdt)

    @staticmethod
    def start():
        game.fsm.demand('Race')

    def load_stuff(self, track_path, car_path, player_cars):
        eng.phys.init()
        player_cars = player_cars[1::2]
        dev = game.options['development']
        game.player_car_name = car_path

        def load_car():
            cars = RaceLogic.cars[:]
            grid = ['kronos', 'themis', 'diones', 'iapeto']
            cars.remove(car_path)
            ai = dev['ai']

            def load_other_cars():
                if not cars:
                    game.fsm.race.fsm.demand('Countdown')
                    return
                car = cars[0]
                cars.remove(car)
                car_class = Car
                if eng.server.is_active:
                    car_class = NetworkCar  # if car in player_cars else Car
                if eng.client.is_active:
                    car_class = NetworkCar
                s_p = game.track.phys.get_start_pos(grid.index(car))
                pos = s_p[0] + (0, 0, .2)
                hpr = s_p[1]
                func = load_other_cars
                no_p = car not in player_cars
                srv_or_sng = eng.server.is_active or not eng.client.is_active
                car_class = AiCar if no_p and srv_or_sng else car_class
                drv = self.drivers_dct[car]
                new_car = car_class(
                    car, self.coll_path, self.coll_name, pos, hpr, func,
                    self.mdt, game.track.laps, self.keys, self.joystick,
                    self.sounds, self.color_main, self.color, self.font,
                    self.car_path, self.phys_file, self.wheel_names,
                    self.tuning_engine, self.tuning_tires,
                    self.tuning_suspensions, self.road_name, self.base_path,
                    self.model_name, self.damage_paths, self.wheel_gfx_names,
                    self.particle_path, drv.logic.engine, drv.logic.tires,
                    drv.logic.suspensions)
                game.cars += [new_car]
            s_p = game.track.phys.get_start_pos(grid.index(car_path))
            pos = s_p[0] + (0, 0, .2)
            hpr = s_p[1]
            func = load_other_cars
            if ai:
                car_cls = AiCar
            else:
                car_cls = PlayerCar
                if eng.server.is_active:
                    car_cls = PlayerCarServer
                if eng.client.is_active:
                    car_cls = PlayerCarClient
            drv = self.drivers_dct[car_path]
            game.player_car = car_cls(
                car_path, self.coll_path, self.coll_name, pos, hpr, func,
                self.mdt, game.track.laps, self.keys, self.joystick,
                self.sounds, self.color_main, self.color, self.font,
                self.car_path, self.phys_file, self.wheel_names,
                self.tuning_engine, self.tuning_tires, self.tuning_suspensions,
                self.road_name, self.base_path, self.model_name,
                self.damage_paths, self.wheel_gfx_names, self.particle_path,
                drv.logic.engine, drv.logic.tires, drv.logic.suspensions)
            game.cars = []
        game.track = Track(
            track_path, load_car, self.shaders, self.music_path,
            self.coll_track_path, self.unmerged, self.merged, self.ghosts,
            self.corner_names, self.waypoint_names, self.show_waypoints,
            self.weapons, self.weapon_names, self.start_name, self.track_name,
            self.track_path, self.track_model_name, self.empty_name,
            self.anim_name, self.omni_tag, self.thanks, self.sign_name,
            self.camera_vec, self.shadow_src, self.laps)
        self.mdt.track = game.track

    def enter_play(self):
        game.track.gfx.model.reparentTo(eng.gfx.world_np)
        game.player_car.gfx.reparent()
        map(lambda car: car.gfx.reparent(), game.cars)

    def start_play(self):
        eng.phys.start()
        eng.event.attach(self.on_frame)
        self.mdt.event.network_register()
        game.player_car.logic.attach(self.mdt.event.on_wrong_way)
        game.track.audio.music.play()
        cars = [game.player_car] + game.cars
        map(lambda car: car.logic.reset_car(), cars)
        map(lambda car: car.event.start(), cars)
        self.mdt.gui.start()

    def on_frame(self):
        game.track.event.update(game.player_car.gfx.nodepath.get_pos())
        cars = [game.player_car] + game.cars
        positions = [(car.name, car.gfx.nodepath.get_pos())
                     for car in cars]
        game.fsm.race.gui.minimap.update(positions)

    @staticmethod
    def ranking():
        cars = [game.player_car] + game.cars
        info = []
        for car in cars:
            past_wp = car.logic.closest_wp()[0].get_pos()
            wp_num = int(car.logic.closest_wp()[0].get_name()[8:])
            dist = (past_wp - car.gfx.nodepath.get_pos()).length()
            info += [(car.name, len(car.logic.lap_times), wp_num, dist)]
        by_dist = sorted(info, key=lambda val: val[3])
        by_wp_num = sorted(by_dist, key=lambda val: val[2])
        by_laps = sorted(by_wp_num, key=lambda val: val[1])
        return [car[0] for car in reversed(by_laps)]

    def exit_play(self):
        game.track.audio.music.stop()
        game.player_car.logic.detach(self.mdt.event.on_wrong_way)
        game.track.destroy()
        game.player_car.destroy()
        map(lambda car: car.destroy(), game.cars)
        eng.phys.stop()
        eng.gfx.clean()
        eng.event.detach(self.on_frame)


class RaceLogicSinglePlayer(RaceLogic):

    def enter_play(self):
        RaceLogic.enter_play(self)
        self.start_play()


class RaceLogicServer(RaceLogic):

    def enter_play(self):
        RaceLogic.enter_play(self)
        self.ready_clients = []
        eng.server.register_cb(self.process_srv)

    def process_srv(self, data_lst, sender):
        if data_lst[0] == NetMsgs.client_ready:
            ipaddr = sender.getAddress().getIpString()
            eng.log_mgr.log('client ready: ' + ipaddr)
            self.ready_clients += [sender]
            connections = eng.server.connections
            if all(client in self.ready_clients for client in connections):
                self.start_play()
                eng.server.send([NetMsgs.start_race])

    def exit_play(self):
        eng.server.destroy()
        eng.server = None
        RaceLogic.exit_play(self)


class RaceLogicClient(RaceLogic):

    def enter_play(self):
        RaceLogic.enter_play(self)
        eng.client.register_cb(self.process_client)

        def send_ready(task):
            eng.client.send([NetMsgs.client_ready])
            eng.log_mgr.log('sent client ready')
            return task.again
        self.send_tsk = taskMgr.doMethodLater(.5, send_ready, 'send ready')
        # the server could not be listen to this event if it is still
        # loading we should do a global protocol, perhaps

    def process_client(self, data_lst, sender):
        if data_lst[0] == NetMsgs.start_race:
            eng.log_mgr.log('start race')
            taskMgr.remove(self.send_tsk)
            self.start_play()

    def exit_play(self):
        eng.client.destroy()
        eng.client = None
        RaceLogic.exit_play(self)
