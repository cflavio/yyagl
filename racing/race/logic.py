from panda3d.core import Camera, NodePath
from yyagl.gameobject import LogicColleague
from yyagl.racing.track.track import Track
from yyagl.racing.car.ai import CarAiPoller
from yyagl.racing.car.car import AiCar
from yyagl.racing.driver.logic import DriverPlayerLoaderStrategy


class NetMsgs(object):

    client_ready = 100
    begin_race = 101
    client_at_countdown = 102
    start_countdown = 103


class RaceLogic(LogicColleague):

    def __init__(self, mediator, rprops):
        self.load_txt = self.cam_tsk = self.cam_node = self.send_tsk = \
            self.cam_pivot = self.ready_clients = self.preview = \
            self.curr_load_txt = self.track = self.cars = self.load_car = None
        self.player_cars = []
        self.props = rprops
        LogicColleague.__init__(self, mediator)
        self.ai_poller = CarAiPoller()

    def load_stuff(self, car_name, player_car_names):
        r_p = self.props
        self.eng.phys_mgr.reset()
        #player_car_names = player_car_names[1::2]
        self.track = Track(r_p)
        self.track.attach_obs(self.on_track_loaded)
        for driver in self.props.drivers:
            local_mp = not self.eng.client.is_client_active and not self.eng.client.is_server_active
            if local_mp and driver.dprops.car_name == r_p.season_props.player_car_names[0] or \
                    not local_mp and driver.dprops.car_name == r_p.season_props.player_car_name:
                self.load_car = lambda: DriverPlayerLoaderStrategy.load(
                    self.props.season_props.car_names[:],
                    r_p, car_name, self.track, self.mediator,
                    r_p.season_props.player_car_name, player_car_names,
                    self.props.season_props, self.ai_poller, self._on_loaded)
                break
        self.mediator.track = self.track  # facade this

    def _on_loaded(self):
        self.mediator.fsm.demand('Countdown', self.props.season_props)

    def on_track_loaded(self):
        self.cars = []
        self.load_car()

    def enter_play(self):
        self.track.detach_obs(self.on_track_loaded)
        self.track.reparent_to(self.eng.gfx.root)
        list(map(lambda pcar: pcar.reparent(), self.player_cars))
        list(map(lambda car: car.reparent(), self.cars))
        self.set_display_regions()

    def set_display_regions(self):
        list(map(base.win.remove_display_region, base.win.get_active_display_regions()[1:-2]))
        if len(self.player_cars) == 1:
            d_r = [base.win.get_active_display_regions()[0]]
            d_r[0].set_dimensions(0, 1, 0, 1)
        if len(self.player_cars) == 2:
            d_r = [base.win.get_active_display_regions()[0]]
            d_r[0].set_dimensions(0, .5, 0, 1)
            d_r += [base.win.make_display_region(.5, 1, 0, 1)]
            cam_node = Camera('cam')
            cam_np = NodePath(cam_node)
            d_r[-1].set_camera(cam_np)
            cam_np.reparentTo(render)
        if len(self.player_cars) == 3:
            d_r = [base.win.get_active_display_regions()[0]]
            d_r[0].set_dimensions(0, 1, .5, 1)
            d_r += [base.win.make_display_region(0, .5, 0, .5)]
            cam_node = Camera('cam')
            cam_np = NodePath(cam_node)
            d_r[-1].set_camera(cam_np)
            cam_np.reparentTo(render)
            d_r += [base.win.make_display_region(.5, 1, 0, .5)]
            cam_node = Camera('cam')
            cam_np = NodePath(cam_node)
            d_r[-1].set_camera(cam_np)
            cam_np.reparentTo(render)
        if len(self.player_cars) == 4:
            d_r = [base.win.get_active_display_regions()[0]]
            d_r[0].set_dimensions(0, .5, .5, 1)
            d_r += [base.win.make_display_region(.5, 1, .5, 1)]
            cam_node = Camera('cam')
            cam_np = NodePath(cam_node)
            d_r[-1].set_camera(cam_np)
            cam_np.reparentTo(render)
            d_r += [base.win.make_display_region(0, .5, 0, .5)]
            cam_node = Camera('cam')
            cam_np = NodePath(cam_node)
            d_r[-1].set_camera(cam_np)
            cam_np.reparentTo(render)
            d_r += [base.win.make_display_region(.5, 1, 0, .5)]
            cam_node = Camera('cam')
            cam_np = NodePath(cam_node)
            d_r[-1].set_camera(cam_np)
            cam_np.reparentTo(render)
        self.cameras = [dr.get_camera() for dr in d_r]
        self.mediator.event.accept('aspectRatioChanged', self.on_aspect_ratio_changed)
        self.on_aspect_ratio_changed()

    def on_aspect_ratio_changed(self):
        if len(self.player_cars) == 1:
            a_r = base.getAspectRatio()
            list(map(lambda cam: cam.node().get_lens().set_aspect_ratio(a_r), self.cameras))
        if len(self.player_cars) == 2:
            a_r = base.getAspectRatio() / 2.0
            list(map(lambda cam: cam.node().get_lens().set_aspect_ratio(a_r), self.cameras))
        if len(self.player_cars) == 3:
            a_r = base.getAspectRatio() * 2.0
            list(map(lambda cam: cam.node().get_lens().set_aspect_ratio(a_r), self.cameras[:1]))
            a_r = base.getAspectRatio()
            list(map(lambda cam: cam.node().get_lens().set_aspect_ratio(a_r), self.cameras[1:]))
        if len(self.player_cars) == 4:
            a_r = base.getAspectRatio()
            list(map(lambda cam: cam.node().get_lens().set_aspect_ratio(a_r), self.cameras[1:]))

    def start_play(self):
        self.eng.phys_mgr.start()
        self.eng.attach_obs(self.on_frame)
        for player_car in self.player_cars:
            player_car.logic.camera.render_all(self.track.gfx.model)  # workaround for prepare_scene (panda3d 1.9)
        self.track.play_music()
        list(map(lambda car: car.reset_car(), self.all_cars))
        list(map(lambda car: car.start(), self.all_cars))
        list(map(lambda car: car.event.attach(self.on_rotate_all), self.all_cars))
        self.mediator.gui.start()
        ai_cars = [car.name for car in self.all_cars if car.__class__ == AiCar]
        for player_car in self.player_cars:
            if self.is_ai_car(player_car):
                ai_cars += [player_car.name]
        self.ai_poller.set_cars(ai_cars)

    def is_ai_car(self, player_car):
        return self.props.a_i == 1 or self.props.a_i == 2 and player_car.name != self.props.season_props.player_car_names[0]

    def on_rotate_all(self, sender):
        cars = [car for car in self.all_cars if car.name != sender.name]
        list(map(lambda car: car.phys.rotate(), cars))
        list(map(lambda car: car.gfx.set_decorator('rotate_all'), cars))

    @property
    def all_cars(self):
        return self.player_cars + self.cars

    @property
    def nonplayer_cars(self):
        return self.cars

    def min_dist(self, car):
        distances = []
        for _car in [_car for _car in self.all_cars if _car != car]:
            dist = (car.gfx.nodepath.node.get_pos() - _car.gfx.nodepath.node.get_pos()).length()
            distances += [dist]
        return min(distances)

    def on_frame(self):
        self.ai_poller.tick()
        for player_car in self.player_cars:
            self.track.gfx.update(player_car.get_pos())
        positions = [(car.name, car.get_pos()) for car in self.all_cars]
        self.mediator.gui.update_minimap(positions)
        if self.props.a_i and self.props.ai_debug:
            self.track.gfx.set_curr_wp(self.player_cars[0].ai.curr_logic.curr_tgt_wp)  # for debug
        if self.mediator.fsm.getCurrentOrNextState() == 'Play':
            for player_car in self.player_cars:
                player_car.upd_ranking(self.ranking())
                if self.props.a_i and self.props.ai_debug:
                    player_car.gui.ai_panel.curr_wp = player_car.ai.curr_logic.curr_tgt_wp.get_name()[8:]
                    player_car.gui.ai_panel.curr_logic = player_car.ai.curr_logic.__class__.__name__
                    player_car.gui.ai_panel.curr_car_dot_traj = round(player_car.ai.curr_logic.car_dot_traj, 3)
                    player_car.gui.ai_panel.curr_obsts = player_car.ai.front_logic.get_obstacles()
                    player_car.gui.ai_panel.curr_obsts_back = player_car.ai.rear_logic.get_obstacles()
                    player_car.gui.ai_panel.curr_input = player_car.ai.get_input()
                    player_car.gui.upd_ai()

    def ranking(self):
        cars = self.player_cars + self.cars
        info = []
        for car in cars:
            curr_wp = car.last_wp_not_fork()
            past_wp = car.not_fork_wps()[car.not_fork_wps().index(curr_wp) - 1]
            # we consider the past since the current may be in front of the car
            dist = (past_wp.pos - car.get_pos()).length()
            wp_num = car.logic.wp_num
            info += [(car.name, car.laps_num, wp_num, dist)]
        sortfunc = lambda val: (val[1], val[2], val[3])
        ranking_info = list(reversed(sorted(info, key=sortfunc)))
        return [car[0] for car in ranking_info]

    def race_ranking(self):
        cars = self.player_cars + self.cars
        compl_ranking = []
        nlaps = self.props.laps
        for car in [car for car in cars if len(car.lap_times) == nlaps]:
            compl_ranking += [(car.name, sum(car.lap_times))]
        rank = list(sorted(compl_ranking, key=lambda val: val[1]))
        rank = [val[0] for val in rank]
        return rank + [val for val in self.ranking() if val not in rank]

    def exit_play(self):
        self.track.stop_music()
        if self.eng.client:
            self.eng.client.is_server_active = False
            self.eng.client.is_client_active = False
        self.track.destroy()
        list(map(lambda car: car.event.detach(self.on_rotate_all), self.all_cars))
        list(map(lambda car: car.destroy(), self.all_cars))
        self.ai_poller.destroy()
        self.eng.phys_mgr.stop()
        self.eng.clean_gfx()
        self.eng.detach_obs(self.on_frame)


class RaceLogicSinglePlayer(RaceLogic):

    def enter_play(self):
        RaceLogic.enter_play(self)
        self.start_play()


class RaceLogicServer(RaceLogic):

    def __init__(self, mediator, rprops):
        RaceLogic.__init__(self, mediator, rprops)
        self._loaded = False
        self.ready_clients = []
        self.eng.server.register_cb(self.process_srv)
        self.eval_tsk = self.eng.add_task(self.eval_start)

    def _on_loaded(self):
        self._loaded = True
        self.process_srv([None], None)

    def process_srv(self, data_lst, sender):
        if data_lst[0] == NetMsgs.client_ready:
            ipaddr = sender.getpeername()[0]
            self.eng.log('client ready: ' + ipaddr)
            self.ready_clients += [sender]
        if data_lst[0] == NetMsgs.client_at_countdown:
            ipaddr = sender.getpeername()[0]
            self.eng.log('client at countdown: ' + ipaddr)
            self.mediator.fsm.countdown_clients += [sender]

    def eval_start(self, task):
        connections = [conn for conn in self.eng.server.connections]
        if all(client in self.ready_clients for client in connections) and self._loaded:
            self.mediator.fsm.demand('Countdown', self.props.season_props)
            self.start_play()
            self.eng.server.send([NetMsgs.begin_race])
            self.eng.log('sent begin_race')
            self.eval_tsk = self.eng.remove_task(self.eval_tsk)
        return task.cont

    def exit_play(self):
        self.eng.server.destroy()
        #self.eng.client.stop()
        RaceLogic.exit_play(self)

    def destroy(self):
        if self.eval_tsk: self.eval_tsk = self.eng.remove_task(self.eval_tsk)
        self.eng.client.register_rpc('leave_room')
        self.eng.client.leave_room(self.props.season_props.room)
        RaceLogic.destroy(self)


class RaceLogicClient(RaceLogic):

    def _on_loaded(self):
        #self.eng.client.register_cb(self.process_client)
        self.eng.client.attach(self.on_begin_race)
        self.eng.client.attach(self.on_start_countdown)

        def send_ready(task):
            self.eng.client.send(['client_ready'])
            self.eng.log('sent client ready')
            return task.again
        self.send_tsk = taskMgr.doMethodLater(.5, send_ready, 'send ready')
        # the server could not be listen to this event if it is still
        # loading we should do a global protocol, perhaps

    def on_begin_race(self):
        self.eng.log('begin race')
        self.eng.client.detach(self.on_begin_race)
        self.eng.rm_do_later(self.send_tsk)
        self.mediator.fsm.demand('Countdown', self.props.season_props)
        self.start_play()
        self.eng.client.send(['client_at_countdown'])
        self.eng.log('sent client at countdown')

    def on_start_countdown(self):
        self.eng.log('start countdown')
        self.eng.client.detach(self.on_start_countdown)
        self.aux_launch_tsk = self.eng.do_later(.5, self.mediator.fsm.client_start_countdown)
        self.mediator.event.network_register()

    def exit_play(self):
        #self.eng.client.stop()
        if self.eng.server.is_active:
            self.eng.server.destroy()
        RaceLogic.exit_play(self)

    def destroy(self):
        if self.send_tsk:
            self.send_tsk = self.eng.rm_do_later(self.send_tsk)
        self.eng.client.register_rpc('leave_room')
        self.eng.client.leave_room(self.props.season_props.room)
        RaceLogic.destroy(self)
