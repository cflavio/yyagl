from yyagl.gameobject import Logic
from yyagl.engine.network.server import Server
from yyagl.engine.network.client import Client
from yyagl.engine.phys import PhysMgr
from yyagl.racing.track.track import Track, TrackProps
from yyagl.racing.car.car import Car, CarProps, PlayerCar, PlayerCarServer, \
    PlayerCarClient, NetworkCar, AiCar, AiPlayerCar


class NetMsgs(object):

    client_ready = 0
    start_race = 1


class RaceLogic(Logic):

    def __init__(
            self, mdt, racelogic_props):
        self.load_txt = None
        self.cam_tsk = None
        self.cam_node = None
        self.send_tsk = None
        self.cam_pivot = None
        self.ready_clients = None
        self.preview = None
        self.curr_load_txt = None
        self.props = racelogic_props
        self.track = None
        self.cars = None
        self.player_car = None
        Logic.__init__(self, mdt)

    def load_stuff(self, track_path, car_path, player_cars):
        r_p = self.props
        PhysMgr().init()
        player_cars = player_cars[1::2]
        game.player_car_name = car_path

        def load_car():
            cars = r_p.cars[:]
            grid = r_p.grid
            cars.remove(car_path)

            def load_other_cars():
                if not cars:
                    return self.mdt.fsm.demand('Countdown')
                car = cars.pop(0)
                car_class = Car
                if Server().is_active:
                    car_class = NetworkCar  # if car in player_cars else Car
                if Client().is_active:
                    car_class = NetworkCar
                s_p = self.track.get_start_pos(grid.index(car))
                pos, hpr = s_p[0] + (0, 0, .2), s_p[1]
                func = load_other_cars
                no_p = car not in player_cars
                srv_or_sng = Server().is_active or not Client().is_active
                car_class = AiCar if no_p and srv_or_sng else car_class
                drv = r_p.drivers[car]
                car_props = CarProps(
                    car, r_p.coll_path, r_p.coll_name, pos, hpr, func,
                    self.mdt, r_p.laps, r_p.keys, r_p.joystick,
                    r_p.sounds, r_p.color_main, r_p.color, r_p.font,
                    r_p.car_path, r_p.phys_file, r_p.wheel_names,
                    r_p.tuning_engine, r_p.tuning_tires,
                    r_p.tuning_suspensions, r_p.road_name, r_p.model_name,
                    r_p.damage_paths, r_p.wheel_gfx_names, r_p.particle_path,
                    drv.logic.engine, drv.logic.tires, drv.logic.suspensions,
                    r_p.rocket_path, r_p.camera_vec,
                    self.mdt.track.phys.waypoints, r_p.respawn_name,
                    r_p.pitstop_name, r_p.wall_name, r_p.goal_name,
                    r_p.bonus_name, r_p.roads_names, r_p.cars)
                new_car = car_class(car_props)
                game.cars += [new_car]
            s_p = self.track.get_start_pos(grid.index(car_path))
            pos, hpr = s_p[0] + (0, 0, .2), s_p[1]
            func = load_other_cars
            if self.props.a_i:
                car_cls = AiPlayerCar
            else:
                car_cls = PlayerCar
                if Server().is_active:
                    car_cls = PlayerCarServer
                if Client().is_active:
                    car_cls = PlayerCarClient
            drv = r_p.drivers[car_path]
            # pos = LVecBase3f(508, 12, .2)
            car_props = CarProps(
                car_path, r_p.coll_path, r_p.coll_name, pos, hpr, func,
                self.mdt, r_p.laps, r_p.keys, r_p.joystick,
                r_p.sounds, r_p.color_main, r_p.color, r_p.font,
                r_p.car_path, r_p.phys_file, r_p.wheel_names,
                r_p.tuning_engine, r_p.tuning_tires, r_p.tuning_suspensions,
                r_p.road_name, r_p.model_name, r_p.damage_paths,
                r_p.wheel_gfx_names, r_p.particle_path, drv.logic.engine,
                drv.logic.tires, drv.logic.suspensions, r_p.rocket_path,
                r_p.camera_vec, self.mdt.track.phys.waypoints,
                r_p.respawn_name, r_p.pitstop_name, r_p.wall_name,
                r_p.goal_name, r_p.bonus_name, r_p.roads_names, r_p.cars)
            game.player_car = self.player_car = car_cls(car_props)  # remove
            game.cars = self.cars = []  # remove game's reference
        track_props = TrackProps(
            track_path, load_car, r_p.shaders, r_p.music_path,
            r_p.coll_track_path, r_p.unmerged, r_p.merged, r_p.ghosts,
            r_p.corner_names, r_p.waypoint_names, r_p.show_waypoints,
            r_p.weapons, r_p.weapon_names, r_p.start, r_p.track_name,
            r_p.track_path, r_p.track_model_name, r_p.empty_name,
            r_p.anim_name, r_p.omni_tag, r_p.sign_cb, r_p.sign_name,
            r_p.camera_vec, r_p.shadow_src, r_p.laps, r_p.bonus_model,
            r_p.bonus_suff)
        game.track = self.track = Track(track_props)  # remove game.track
        self.mdt.track = self.track  # facade this

    def enter_play(self):
        self.track.gfx.model.reparentTo(eng.gfx.root)
        self.player_car.gfx.reparent()
        map(lambda car: car.gfx.reparent(), self.cars)

    def start_play(self):
        PhysMgr().start()
        eng.attach_obs(self.on_frame)
        self.mdt.event.network_register()
        self.player_car.attach_obs(self.mdt.event.on_wrong_way)
        self.track.play_music()
        cars = [self.player_car] + self.cars
        map(lambda car: car.reset_car(), cars)
        map(lambda car: car.start(), cars)
        self.mdt.gui.start()

    def on_frame(self):
        self.track.update(self.player_car.get_pos())
        cars = [self.player_car] + self.cars
        positions = [(car.name, car.get_pos()) for car in cars]
        self.mdt.gui.update_minimap(positions)

    def ranking(self):
        cars = [self.player_car] + self.cars
        info = []
        for car in cars:
            past_wp = car.logic.last_wp_not_fork()
            try:
                wp_num = car.logic.wps_not_fork().index(past_wp)
            except ValueError:  # if the track has not a goal
                return [car.name for car in cars]
            first_lap = not len(car.lap_times)
            wpnf = wp_num == len(car.logic.wps_not_fork()) - 1
            if first_lap and wpnf and len(car.logic.waypoints) <= 1:
                wp_num = -1
            dist = (past_wp.get_pos() - car.get_pos()).length()
            info += [(car.name, len(car.lap_times), wp_num, dist)]
        sortfunc = lambda val: (val[1], val[2], val[3])
        by_laps = list(reversed(sorted(info, key=sortfunc)))
        return [car[0] for car in by_laps]

    def race_ranking(self):
        ranking = self.ranking()
        cars = [self.player_car] + self.cars
        compl_ranking = []
        for car in cars:
            if len(car.lap_times) == self.props.laps:
                compl_ranking += [(car.name, sum(car.lap_times))]
        rank = list(sorted(compl_ranking, key=lambda val: val[1]))
        rank = [val[0] for val in rank]
        ranking = [val for val in ranking if val not in rank]
        return rank + ranking

    def exit_play(self):
        self.track.stop_music()
        self.player_car.detach_obs(self.mdt.event.on_wrong_way)
        self.player_car.attach_obs(self.mdt.event.on_respawn)
        self.track.destroy()
        self.player_car.destroy()
        map(lambda car: car.destroy(), self.cars)
        PhysMgr().stop()
        eng.clean_gfx()
        eng.detach_obs(self.on_frame)


class RaceLogicSinglePlayer(RaceLogic):

    def enter_play(self):
        RaceLogic.enter_play(self)
        self.start_play()


class RaceLogicServer(RaceLogic):

    def enter_play(self):
        RaceLogic.enter_play(self)
        self.ready_clients = []
        eng.register_server_cb(self.process_srv)

    def process_srv(self, data_lst, sender):
        if data_lst[0] == NetMsgs.client_ready:
            ipaddr = sender.getAddress().getIpString()
            eng.log('client ready: ' + ipaddr)
            self.ready_clients += [sender]
            connections = Server().connections
            if all(client in self.ready_clients for client in connections):
                self.start_play()
                Server().send([NetMsgs.start_race])

    def exit_play(self):
        Server().destroy()
        RaceLogic.exit_play(self)


class RaceLogicClient(RaceLogic):

    def enter_play(self):
        RaceLogic.enter_play(self)
        eng.register_client_cb(self.process_client)

        def send_ready(task):
            Client().send([NetMsgs.client_ready])
            eng.log('sent client ready')
            return task.again
        self.send_tsk = taskMgr.doMethodLater(.5, send_ready, 'send ready')
        # the server could not be listen to this event if it is still
        # loading we should do a global protocol, perhaps

    def process_client(self, data_lst, sender):
        if data_lst[0] == NetMsgs.start_race:
            eng.log('start race')
            taskMgr.remove(self.send_tsk)
            self.start_play()

    def exit_play(self):
        Client().destroy()
        RaceLogic.exit_play(self)
