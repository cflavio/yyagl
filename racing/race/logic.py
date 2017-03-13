from yyagl.gameobject import Logic
from yyagl.racing.track.track import Track
from yyagl.racing.car.car import Car, PlayerCar, PlayerCarServer, \
    PlayerCarClient, NetworkCar, AiCar


class NetMsgs(object):

    client_ready = 0
    start_race = 1


class RaceLogic(Logic):

    def __init__(
            self, mdt, race_props):
        self.load_txt = None
        self.cam_tsk = None
        self.cam_node = None
        self.send_tsk = None
        self.cam_pivot = None
        self.ready_clients = None
        self.preview = None
        self.curr_load_txt = None
        self.race_props = race_props
        Logic.__init__(self, mdt)

    def load_stuff(self, track_path, car_path, player_cars):
        r_p = self.race_props
        eng.phys.init()
        player_cars = player_cars[1::2]
        game.player_car_name = car_path

        def load_car():
            cars = r_p.cars[:]
            grid = ['kronos', 'themis', 'diones', 'iapeto']  # pass the grid
            cars.remove(car_path)

            def load_other_cars():
                if not cars:
                    self.mdt.fsm.demand('Countdown')
                    return
                car = cars.pop(0)
                car_class = Car
                if eng.server.is_active:
                    car_class = NetworkCar  # if car in player_cars else Car
                if eng.client.is_active:
                    car_class = NetworkCar
                s_p = game.track.phys.get_start_pos(grid.index(car))
                pos, hpr = s_p[0] + (0, 0, .2), s_p[1]
                func = load_other_cars
                no_p = car not in player_cars
                srv_or_sng = eng.server.is_active or not eng.client.is_active
                car_class = AiCar if no_p and srv_or_sng else car_class
                drv = r_p.drivers[car]
                new_car = car_class(
                    car, r_p.coll_path, r_p.coll_name, pos, hpr, func,
                    self.mdt, game.track.laps, r_p.keys, r_p.joystick,
                    r_p.sounds, r_p.color_main, r_p.color, r_p.font,
                    r_p.car_path, r_p.phys_file, r_p.wheel_names,
                    r_p.tuning_engine, r_p.tuning_tires,
                    r_p.tuning_suspensions, r_p.road_name, r_p.base_path,
                    r_p.model_name, r_p.damage_paths, r_p.wheel_gfx_names,
                    r_p.particle_path, drv.logic.engine, drv.logic.tires,
                    drv.logic.suspensions, r_p.rocket_path, r_p.camera_vec,
                    self.mdt.track.phys.waypoints)
                game.cars += [new_car]
            s_p = game.track.phys.get_start_pos(grid.index(car_path))
            pos, hpr = s_p[0] + (0, 0, .2), s_p[1]
            func = load_other_cars
            if self.race_props.ai:
                car_cls = AiCar
            else:
                car_cls = PlayerCar
                if eng.server.is_active:
                    car_cls = PlayerCarServer
                if eng.client.is_active:
                    car_cls = PlayerCarClient
            drv = r_p.drivers[car_path]
            game.player_car = car_cls(
                car_path, r_p.coll_path, r_p.coll_name, pos, hpr, func,
                self.mdt, game.track.laps, r_p.keys, r_p.joystick,
                r_p.sounds, r_p.color_main, r_p.color, r_p.font,
                r_p.car_path, r_p.phys_file, r_p.wheel_names,
                r_p.tuning_engine, r_p.tuning_tires, r_p.tuning_suspensions,
                r_p.road_name, r_p.base_path, r_p.model_name,
                r_p.damage_paths, r_p.wheel_gfx_names, r_p.particle_path,
                drv.logic.engine, drv.logic.tires, drv.logic.suspensions,
                r_p.rocket_path, r_p.camera_vec, self.mdt.track.phys.waypoints)
            game.cars = []
        game.track = Track(
            track_path, load_car, r_p.shaders, r_p.music_path,
            r_p.coll_track_path, r_p.unmerged, r_p.merged, r_p.ghosts,
            r_p.corner_names, r_p.waypoint_names, r_p.show_waypoints,
            r_p.weapons, r_p.weapon_names, r_p.start, r_p.track_name,
            r_p.track_path, r_p.track_model_name, r_p.empty_name,
            r_p.anim_name, r_p.omni_tag, r_p.thanks, r_p.sign_name,
            r_p.camera_vec, r_p.shadow_src, r_p.laps, r_p.bonus_name,
            r_p.bonus_suff)
        self.mdt.track = game.track

    def enter_play(self):
        # race must have ref to these
        game.track.gfx.model.reparentTo(eng.gfx.world_np)
        game.player_car.gfx.reparent()
        map(lambda car: car.gfx.reparent(), game.cars)

    def start_play(self):
        eng.phys.start()
        eng.event.attach(self.on_frame)
        self.mdt.event.network_register()
        # race must have ref to these
        game.player_car.logic.attach(self.mdt.event.on_wrong_way)
        game.track.audio.music.play()
        cars = [game.player_car] + game.cars
        map(lambda car: car.logic.reset_car(), cars)
        map(lambda car: car.event.start(), cars)
        self.mdt.gui.start()

    def on_frame(self):
        # race must have ref to these
        game.track.event.update(game.player_car.gfx.nodepath.get_pos())
        cars = [game.player_car] + game.cars
        positions = [(car.name, car.gfx.nodepath.get_pos())
                     for car in cars]
        self.mdt.gui.minimap.update(positions)

    @staticmethod
    def ranking():
        cars = [game.player_car] + game.cars  # race must have ref to these
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
        # race must have ref to these
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
