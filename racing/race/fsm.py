from logging import info
from yyagl.gameobject import FsmColleague
from yyagl.racing.race.logic import NetMsgs
from yyagl.racing.race.gui.countdown import Countdown
from yyagl.racing.player.player import Player


class RaceFsm(FsmColleague):

    def __init__(self, mediator, shaders):
        self.countdown = None
        self.shaders = shaders
        self.menu_props = None
        self.countdown_sfx = None
        FsmColleague.__init__(self, mediator)
        self.defaultTransitions = {
            'Loading': ['Countdown'],
            'Countdown': ['Play'],
            'Play': ['Results']}

    def enterLoading(self, rprops, track_name_transl, ranking, players):
        info('entering Loading state')
        self.menu_props = rprops.season_props.gameprops.menu_props
        self.countdown_sfx = rprops.season_props.countdown_sfx
        self.mediator.gui.loading.enter_loading(rprops, track_name_transl, ranking, players)
        player_car_names = [player.car for player in players if player.kind == Player.human]
        player_car_name = player_car_names[0]
        args = [player_car_name, player_car_names, players]
        self.eng.do_later(1.0, self.mediator.logic.load_stuff, args)

    def exitLoading(self):
        info('exiting Loading state')
        self.mediator.gui.loading.exit_loading()
        self.mediator.event.notify('on_race_loaded')
        # eng.set_cam_pos((0, 0, 0))
        if not all(self.mediator.logic.player_cars): return  # we've closed the window
        for player_car in self.mediator.logic.player_cars:
            player_car.attach_obs(self.mediator.event.on_end_race)

    def enterCountdown(self, sprops):
        info('entering Countdown state')
        self.eng.hide_cursor()
        self.sprops = sprops
        self.mediator.event.register_menu()
        self.mediator.logic.enter_play()
        if self.shaders:
            self.eng.shader_mgr.toggle_shader()
        cars = self.mediator.logic.player_cars + self.mediator.logic.cars
        list(map(lambda car: car.reset_car(), cars))
        list(map(lambda car: car.demand('Countdown'), cars))
        self.aux_launch_tsk = None
        self.launch_tsk = self.eng.do_later(
            sprops.race_start_time, self.aux_start_countdown)

    def aux_start_countdown(self):
        # i think it's necessary since otherwise panda may use invoking's time
        # so it may be already elapsed.
        self.aux_launch_tsk = self.eng.do_later(.5, self.start_countdown)

    def start_countdown(self):
        self.countdown = Countdown(self.countdown_sfx, self.menu_props.font,
                                   self.sprops.countdown_seconds)
        self.lmb_call = lambda: self.demand('Play')
        self.countdown.attach(self.lmb_call, rename='on_start_race')

    def exitCountdown(self):
        info('exiting Countdown state')
        if self.countdown:
            self.countdown.detach('on_start_race', self.lmb_call)
            self.countdown.destroy()
        self.lmb_call = None
        self.eng.rm_do_later(self.launch_tsk)
        if self.aux_launch_tsk: self.eng.rm_do_later(self.aux_launch_tsk)
        # eng.do_later(.5, game.player_car.gfx.apply_damage)
        # eng.do_later(.6, game.player_car.gfx.apply_damage)
        # eng.gfx.print_stats()
        if self.getCurrentOrNextState() != 'Play':
            self.mediator.logic.exit_play()

    def enterPlay(self):
        info('entering Play state')
        cars = self.mediator.logic.player_cars + self.mediator.logic.cars
        list(map(lambda car: car.demand('Play'), cars))

    def exitPlay(self):
        info('exiting Play state')
        RaceFsm.eng.show_cursor()
        if self.getCurrentOrNextState() != 'Results':
            self.mediator.logic.exit_play()

    def enterResults(self, race_ranking, players):
        self.mediator.gui.results.show(
            race_ranking, self.mediator.logic.player_cars[0].lap_times, players)
        cars = self.mediator.logic.player_cars + self.mediator.logic.cars
        list(map(lambda car: car.demand('Results'), cars))

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

    def start_countdown(self): self._countdown_ready = True

    def server_start_countdown(self): RaceFsm.start_countdown(self)

    def eval_start(self, task):
        connections = [conn for conn in self.eng.server.connections]
        if all(client in self.countdown_clients for client in connections) and self._countdown_ready:
            self.eng.server.send([NetMsgs.start_countdown])
            self.eval_tsk = self.eng.remove_task(self.eval_tsk)
            self.aux_launch_tsk = self.eng.do_later(.5, self.server_start_countdown)
            self.mediator.event.network_register()
        return task.cont


class RaceFsmClient(RaceFsm):

    def __init__(self, mediator, shaders):
        RaceFsm.__init__(self, mediator, shaders)

    def start_countdown(self): pass

    def client_start_countdown(self): RaceFsm.start_countdown(self)
