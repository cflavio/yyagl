from yyagl.gameobject import Logic
from yyagl.racing.track.track import Track, TrackProps
from yyagl.racing.car.car import Car, CarProps, PlayerCar, PlayerCarServer, \
    PlayerCarClient, NetworkCar, AiCar, AiPlayerCar
from panda3d.core import LVecBase3f


class NetMsgs(object):

    client_ready = 0
    start_race = 1


class RaceLogicProps(object):

    def __init__(
            self, shaders, music_path, coll_track_path, unmerged, merged,
            ghosts, corner_names, waypoint_names, show_waypoints, weapons,
            weapon_names, start, track_name, track_path, track_model_name,
            empty_name, anim_name, omni_tag, sign_cb, sign_name, camera_vec,
            shadow_src, laps, bonus_model, bonus_suff, cars, a_i, drivers,
            coll_path, coll_name, keys, joystick, sounds, color_main, color,
            font, car_path, phys_file, wheel_names, tuning_engine,
            tuning_tires, tuning_suspensions, road_name, model_name,
            damage_paths, wheel_gfx_names, particle_path, rocket_path,
            respawn_name, pitstop_name, wall_name, goal_name, bonus_name,
            roads_names, grid):
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
        self.start = start
        self.track_name = track_name
        self.track_path = track_path
        self.track_model_name = track_model_name
        self.empty_name = empty_name
        self.anim_name = anim_name
        self.omni_tag = omni_tag
        self.sign_cb = sign_cb
        self.sign_name = sign_name
        self.camera_vec = camera_vec
        self.shadow_src = shadow_src
        self.laps = laps
        self.bonus_model = bonus_model
        self.bonus_suff = bonus_suff
        self.cars = cars
        self.a_i = a_i
        self.drivers = drivers
        self.coll_path = coll_path
        self.coll_name = coll_name
        self.keys = keys
        self.joystick = joystick
        self.sounds = sounds
        self.color_main = color_main
        self.color = color
        self.font = font
        self.car_path = car_path
        self.phys_file = phys_file
        self.wheel_names = wheel_names
        self.tuning_engine = tuning_engine
        self.tuning_tires = tuning_tires
        self.tuning_suspensions = tuning_suspensions
        self.road_name = road_name
        self.model_name = model_name
        self.damage_paths = damage_paths
        self.wheel_gfx_names = wheel_gfx_names
        self.particle_path = particle_path
        self.rocket_path = rocket_path
        self.respawn_name = respawn_name
        self.pitstop_name = pitstop_name
        self.wall_name = wall_name
        self.goal_name = goal_name
        self.bonus_name = bonus_name
        self.roads_names = roads_names
        self.grid = grid


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
        eng.init_phys()
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
                if eng.is_server_active:
                    car_class = NetworkCar  # if car in player_cars else Car
                if eng.is_client_active:
                    car_class = NetworkCar
                s_p = self.track.get_start_pos(grid.index(car))
                pos, hpr = s_p[0] + (0, 0, .2), s_p[1]
                func = load_other_cars
                no_p = car not in player_cars
                srv_or_sng = eng.is_server_active or not eng.is_client_active
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
                if eng.is_server_active:
                    car_cls = PlayerCarServer
                if eng.is_client_active:
                    car_cls = PlayerCarClient
            drv = r_p.drivers[car_path]
            #pos = LVecBase3f(508, 12, .2)
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
        self.track.gfx.model.reparentTo(eng.gfx.world_np)
        self.player_car.gfx.reparent()
        map(lambda car: car.gfx.reparent(), self.cars)

    def start_play(self):
        eng.start_phys()
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
            wp_num = car.logic.wps_not_fork().index(past_wp)
            if not len(car.lap_times) and wp_num == len(car.logic.wps_not_fork()) - 1 and len(car.logic.waypoints) <= 1:
                wp_num = -1
            dist = (past_wp.get_pos() - car.get_pos()).length()
            info += [(car.name, len(car.lap_times), wp_num, dist)]
        by_laps = list(reversed(sorted(info, key=lambda val: (val[1], val[2], val[3]))))
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
        eng.stop_phys()
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
            connections = eng.server_connections
            if all(client in self.ready_clients for client in connections):
                self.start_play()
                eng.server_send([NetMsgs.start_race])

    def exit_play(self):
        eng.server = eng.destroy_server()
        RaceLogic.exit_play(self)


class RaceLogicClient(RaceLogic):

    def enter_play(self):
        RaceLogic.enter_play(self)
        eng.register_client_cb(self.process_client)

        def send_ready(task):
            eng.client_send([NetMsgs.client_ready])
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
        eng.client = eng.destroy_client()
        RaceLogic.exit_play(self)
