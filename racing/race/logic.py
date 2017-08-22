from yyagl.gameobject import Logic
from yyagl.engine.network.server import Server
from yyagl.engine.network.client import Client
from yyagl.engine.phys import PhysMgr
from yyagl.racing.track.track import Track
from yyagl.racing.car.car import Car, CarProps, CarPlayer, CarPlayerServer, \
    CarPlayerClient, NetworkCar, AiCar, AiCarPlayer


class NetMsgs(object):

    client_ready = 0
    start_race = 1


class CarLoaderStrategy(object):

    @staticmethod
    def load(cars, r_p, car_name, track, race, player_car_names, s_p):
        if not cars:
            return race.fsm.demand('Countdown')
        car = cars.pop(0)
        car_cls = Car
        if Server().is_active or Client().is_active:
            car_cls = NetworkCar  # if car in player_cars else Car
        no_p = car not in player_car_names
        srv_or_sng = Server().is_active or not Client().is_active
        car_cls = AiCar if no_p and srv_or_sng else car_cls
        game.cars += [CarLoaderStrategy.actual_load(
            cars, car, r_p, track, race, car_cls, player_car_names, s_p)]

    @staticmethod
    def actual_load(cars, load_car_name, r_p, track, race, car_cls,
                    player_car_names, seas_p):
        drv = r_p.drivers[load_car_name]
        s_p = track.get_start_pos(r_p.grid.index(load_car_name))
        pos, hpr = s_p[0] + (0, 0, .2), s_p[1]
        car_props = CarProps(
            load_car_name, pos, hpr,
            lambda: CarLoaderStrategy.load(cars, r_p, load_car_name, track,
                                           race, player_car_names, seas_p),
            race, drv.dprops.f_engine, drv.dprops.f_tires,
            drv.dprops.f_suspensions, race.track.phys.wp2prevs)
        return car_cls(car_props, r_p, seas_p)


class CarPlayerLoaderStrategy(object):

    @staticmethod
    def load(r_p, car_name, track, race, player_car_names, s_p):
        cars = [car for car in r_p.cars if car != car_name]
        if r_p.a_i:
            car_cls = AiCarPlayer
        else:
            car_cls = CarPlayer
            if Server().is_active:
                car_cls = CarPlayerServer
            if Client().is_active:
                car_cls = CarPlayerClient
        game.player_car = CarLoaderStrategy.actual_load(
            cars, car_name, r_p, track, race, car_cls, player_car_names, s_p)


class RaceLogic(Logic):

    def __init__(self, mdt, rprops, sprops):
        self.load_txt = self.cam_tsk = self.cam_node = self.send_tsk = \
            self.cam_pivot = self.ready_clients = self.preview = \
            self.curr_load_txt = self.track = self.cars = self.player_car = \
            self.load_car = None
        self.props = rprops
        self.sprops = sprops
        Logic.__init__(self, mdt)

    def load_stuff(self, car_name, player_car_names):
        r_p = self.props
        PhysMgr().init()
        player_car_names = player_car_names[1::2]
        game.player_car_name = car_name
        game.track = self.track = Track(r_p)  # remove game.track
        game.track.attach_obs(self.on_track_loaded)
        self.load_car = lambda: CarPlayerLoaderStrategy.load(
            r_p, car_name, self.track, self.mdt, player_car_names, self.sprops)
        self.mdt.track = self.track  # facade this

    def on_track_loaded(self):
        self.load_car()
        game.cars = self.cars = []  # remove game's reference
        self.player_car = game.player_car  # remove

    def enter_play(self):
        game.track.detach_obs(self.on_track_loaded)
        self.track.reparent_to(eng.gfx.root)
        self.player_car.reparent()
        map(lambda car: car.reparent(), self.cars)

    def start_play(self):
        PhysMgr().start()
        eng.attach_obs(self.on_frame)
        self.mdt.event.network_register()
        self.player_car.attach_obs(self.mdt.event.on_wrong_way)
        self.track.play_music()
        map(lambda car: car.reset_car(), self.all_cars)
        map(lambda car: car.start(), self.all_cars)
        self.mdt.gui.start()

    @property
    def all_cars(self):
        return [self.player_car] + self.cars

    @property
    def nonplayer_cars(self):
        return self.cars

    def on_frame(self):
        self.track.update(self.player_car.get_pos())
        positions = [(car.name, car.get_pos()) for car in self.all_cars]
        self.mdt.gui.update_minimap(positions)

    def ranking(self):
        cars = [self.player_car] + self.cars
        info = []
        for car in cars:
            curr_wp = car.last_wp_not_fork()
            past_wp = car.not_fork_wps()[car.not_fork_wps().index(curr_wp) - 1]
            # we consider the past since the current may be in front of the car
            dist = (past_wp.get_pos() - car.get_pos()).length()
            wp_num = car.logic.wp_num
            info += [(car.name, car.laps_num, wp_num, dist)]
        sortfunc = lambda val: (val[1], val[2], val[3])
        ranking_info = list(reversed(sorted(info, key=sortfunc)))
        return [car[0] for car in ranking_info]

    def race_ranking(self):
        cars = [self.player_car] + self.cars
        compl_ranking = []
        nlaps = self.props.laps
        for car in [car for car in cars if len(car.lap_times) == nlaps]:
            compl_ranking += [(car.name, sum(car.lap_times))]
        rank = list(sorted(compl_ranking, key=lambda val: val[1]))
        rank = [val[0] for val in rank]
        return rank + [val for val in self.ranking() if val not in rank]

    def exit_play(self):
        self.track.stop_music()
        self.player_car.detach_obs(self.mdt.event.on_wrong_way)
        self.track.destroy()
        map(lambda car: car.destroy(), self.all_cars)
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
            ipaddr = sender.get_address().get_ip_string()
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
        self.send_tsk = eng.do_later(.5, send_ready)
        # the server could not be listen to this event if it is still
        # loading we should do a global protocol, perhaps

    def process_client(self, data_lst, sender):
        if data_lst[0] == NetMsgs.start_race:
            eng.log('start race')
            eng.remove_do_later(self.send_tsk)
            self.start_play()

    def exit_play(self):
        Client().destroy()
        RaceLogic.exit_play(self)
