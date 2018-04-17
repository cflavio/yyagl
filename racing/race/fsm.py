from yyagl.gameobject import FsmColleague
from yyagl.racing.race.logic import NetMsgs
from yyagl.racing.race.gui.countdown import Countdown


class RaceFsm(FsmColleague):

    def __init__(self, mediator, shaders):
        self.countdown = None
        self.shaders = shaders
        self.menu_args = None
        self.countdown_sfx = None
        FsmColleague.__init__(self, mediator)
        self.defaultTransitions = {
            'Loading': ['Countdown'],
            'Countdown': ['Play'],
            'Play': ['Results']}

    def enterLoading(self, rprops, track_name_transl, drivers, ranking, tuning):
        self.eng.log_mgr.log('entering Loading state')
        self.menu_args = rprops.season_props.gameprops.menu_args
        self.countdown_sfx = rprops.season_props.countdown_sfx
        self.mediator.gui.loading.enter_loading(rprops, track_name_transl, drivers,
                                           ranking, tuning)
        args = [rprops.season_props.player_car_name, rprops.season_props.player_car_names]
        self.eng.do_later(1.0, self.mediator.logic.load_stuff, args)

    def exitLoading(self):
        self.eng.log_mgr.log('exiting Loading state')
        self.mediator.gui.loading.exit_loading()
        self.mediator.event.notify('on_race_loaded')
        # eng.set_cam_pos((0, 0, 0))
        self.mediator.logic.player_car.attach_obs(self.mediator.event.on_wrong_way)
        self.mediator.logic.player_car.attach_obs(self.mediator.event.on_end_race)

    def enterCountdown(self, sprops):
        self.eng.log_mgr.log('entering Countdown state')
        self.eng.hide_cursor()
        self.sprops = sprops
        self.mediator.event.register_menu()
        self.mediator.logic.enter_play()
        if self.shaders:
            self.eng.shader_mgr.toggle_shader()
        cars = [self.mediator.logic.player_car] + self.mediator.logic.cars
        map(lambda car: car.reset_car(), cars)
        map(lambda car: car.demand('Countdown'), cars)
        self.aux_launch_tsk = self.aux_aux_launch_tsk = None
        self.launch_tsk = self.eng.do_later(
            sprops.race_start_time, self.aux_start_countdown)

    def aux_start_countdown(self):
        # i think it's necessary since otherwise panda may use invoking's time
        # so it may be already elapsed.
        self.aux_launch_tsk = self.eng.do_later(.5, self.start_countdown)

    def start_countdown(self):
        self.countdown = Countdown(self.countdown_sfx, self.menu_args.font,
                                   self.sprops.countdown_seconds)
        self.countdown.attach(lambda: self.demand('Play'),
                              rename='on_start_race')

    def exitCountdown(self):
        self.eng.log_mgr.log('exiting Countdown state')
        if self.countdown: self.countdown.destroy()
        self.eng.remove_do_later(self.launch_tsk)
        if self.aux_launch_tsk: self.eng.remove_do_later(self.aux_launch_tsk)
        if self.aux_aux_launch_tsk: self.eng.remove_do_later(self.aux_aux_launch_tsk)
        # eng.do_later(.5, game.player_car.gfx.apply_damage)
        # eng.do_later(.6, game.player_car.gfx.apply_damage)
        # eng.gfx.print_stats()

    def enterPlay(self):
        self.eng.log_mgr.log('entering Play state')
        cars = [self.mediator.logic.player_car] + self.mediator.logic.cars
        map(lambda car: car.demand('Play'), cars)

    def exitPlay(self):
        RaceFsm.eng.log_mgr.log('exiting Play state')
        RaceFsm.eng.show_cursor()
        if self.getCurrentOrNextState() != 'Results':
            self.mediator.logic.exit_play()

    def enterResults(self, race_ranking):
        self.mediator.gui.results.show(
            race_ranking, self.mediator.logic.player_car.lap_times,
            self.mediator.logic.drivers)
        cars = [self.mediator.logic.player_car] + self.mediator.logic.cars
        map(lambda car: car.demand('Results'), cars)

    def exitResults(self):
        self.mediator.logic.exit_play()
        if self.shaders:
            self.eng.toggle_shader()


class RaceFsmServer(RaceFsm):

    def __init__(self, mediator, shaders):
        RaceFsm.__init__(self, mediator, shaders)
        self._countdown_ready = False
        self.countdown_clients = []
        self.eval_tsk = self.eng.add_task(self.eval_start)

    def aux_start_countdown(self):
        self._countdown_ready = True

    def eval_start(self, task):
        connections = [conn[0] for conn in self.eng.server.connections]
        if all(client in self.countdown_clients for client in connections) and self._countdown_ready:
            self.eng.server.send([NetMsgs.start_countdown])
            self.eval_tsk = self.eng.remove_task(self.eval_tsk)
            self.aux_launch_tsk = self.eng.do_later(.5, self.start_countdown)
            self.mediator.event.network_register()
        return task.cont


class RaceFsmClient(RaceFsm):

    def __init__(self, mediator, shaders):
        RaceFsm.__init__(self, mediator, shaders)

    def aux_start_countdown(self):
        # i think it's necessary since otherwise panda may use invoking's time
        # so it may be already elapsed.
        self.aux_aux_launch_tsk = self.eng.do_later(.3, self.aux_aux_start_countdown)

    def aux_aux_start_countdown(self):
        self.eng.client.send([NetMsgs.client_at_countdown])
        self.eng.log('sent client at countdown')
