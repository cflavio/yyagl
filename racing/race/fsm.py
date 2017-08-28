from yyagl.gameobject import Fsm
from yyagl.engine.log import LogMgr
from yyagl.engine.shader import ShaderMgr
from yyagl.racing.race.gui.countdown import Countdown


class RaceFsm(Fsm):

    def __init__(self, mdt, shaders):
        self.countdown = None
        self.shaders = shaders
        self.menu_args = None
        self.countdown_sfx = None
        Fsm.__init__(self, mdt)
        self.defaultTransitions = {
            'Loading': ['Countdown'],
            'Countdown': ['Play'],
            'Play': ['Results']}

    def enterLoading(self, rprops, sprops, track_name_transl, drivers):
        LogMgr().log('entering Loading state')
        self.menu_args = rprops.menu_args
        self.countdown_sfx = sprops.countdown_sfx
        self.mdt.gui.loading.enter_loading(rprops, sprops, track_name_transl,
                                           drivers)
        args = [rprops.player_car_name, []]
        eng.do_later(1.0, self.mdt.logic.load_stuff, args)

    def exitLoading(self):
        LogMgr().log('exiting Loading state')
        self.mdt.gui.loading.exit_loading()
        self.mdt.event.notify('on_race_loaded')
        # eng.set_cam_pos((0, 0, 0))
        self.mdt.logic.player_car.attach_obs(self.mdt.event.on_wrong_way)
        self.mdt.logic.player_car.attach_obs(self.mdt.event.on_end_race)

    def enterCountdown(self, sprops):
        LogMgr().log('entering Countdown state')
        eng.hide_cursor()
        self.mdt.event.register_menu()
        self.mdt.logic.enter_play()
        if self.shaders:
            ShaderMgr().toggle_shader()
        eng.do_later(sprops.race_start_time,
                     self.aux_start_countdown, [sprops.countdown_seconds])
        cars = [self.mdt.logic.player_car] + self.mdt.logic.cars
        map(lambda car: car.demand('Countdown'), cars)

    def aux_start_countdown(self, countdown_seconds):
        # i think it's necessary since otherwise panda may use invoking's time
        # so it may be already elapsed.
        eng.do_later(.5, self.start_countdown, [countdown_seconds])

    def start_countdown(self, countdown_seconds):
        self.countdown = Countdown(self.countdown_sfx, self.menu_args.font,
                                   countdown_seconds)
        self.countdown.attach(lambda: self.demand('Play'),
                              rename='on_start_race')

    def exitCountdown(self):
        LogMgr().log('exiting Countdown state')
        self.countdown.destroy()
        # eng.do_later(.5, game.player_car.gfx.apply_damage)
        # eng.do_later(.6, game.player_car.gfx.apply_damage)
        # eng.gfx.print_stats()

    def enterPlay(self):
        LogMgr().log('entering Play state')
        cars = [self.mdt.logic.player_car] + self.mdt.logic.cars
        map(lambda car: car.demand('Play'), cars)

    @staticmethod
    def exitPlay():
        LogMgr().log('exiting Play state')
        eng.show_cursor()

    def enterResults(self, race_ranking):
        self.mdt.gui.results.show(
            race_ranking, self.mdt.logic.player_car.lap_times,
            self.mdt.logic.drivers)
        cars = [self.mdt.logic.player_car] + self.mdt.logic.cars
        map(lambda car: car.demand('Results'), cars)

    def exitResults(self):
        self.mdt.logic.exit_play()
        if self.shaders:
            eng.toggle_shader()
