from yyagl.gameobject import Fsm
from yyagl.engine.log import LogMgr
from yyagl.engine.shader import ShaderMgr
from yyagl.racing.race.gui.countdown import Countdown
from .gui.loading.loading import LoadingProps


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

    def enterLoading(
            self, track_path, car_path, player_cars, drivers, tracks,
            track_name_transl, single_race, grid, cars_path, drivers_path,
            joystick, keys, menu_args, countdown_sfx):
        LogMgr().log('entering Loading state')
        self.menu_args = menu_args
        self.countdown_sfx = countdown_sfx
        loading_props = LoadingProps(
            track_path, car_path, drivers, tracks, track_name_transl,
            single_race, grid, cars_path, drivers_path, joystick, keys,
            menu_args)
        self.mdt.gui.loading.enter_loading(loading_props)
        args = [track_path, car_path, player_cars]
        eng.do_later(1.0, self.mdt.logic.load_stuff, args)

    def exitLoading(self):
        LogMgr().log('exiting Loading state')
        self.mdt.gui.loading.exit_loading()
        self.mdt.event.notify('on_race_loaded')
        #eng.set_cam_pos((0, 0, 0))
        self.mdt.logic.player_car.attach_obs(self.mdt.event.on_wrong_way)
        self.mdt.logic.player_car.attach_obs(self.mdt.event.on_respawn)
        self.mdt.logic.player_car.attach_obs(self.mdt.event.on_end_race)

    def enterCountdown(self):
        eng.hide_cursor()
        self.mdt.event.register_menu()
        self.countdown = Countdown(self.countdown_sfx, self.menu_args.font)
        self.countdown.attach(self.on_start_race)
        self.mdt.logic.enter_play()
        if self.shaders:
            ShaderMgr().toggle_shader()
        cars = [self.mdt.logic.player_car] + self.mdt.logic.cars
        map(lambda car: car.demand('Countdown'), cars)

    def exitCountdown(self):
        self.countdown.destroy()
        #eng.do_later(.5, game.player_car.gfx.apply_damage)
        #eng.do_later(.6, game.player_car.gfx.apply_damage)
        #eng.gfx.print_stats()

    def enterPlay(self):
        LogMgr().log('entering Play state')
        cars = [self.mdt.logic.player_car] + self.mdt.logic.cars
        map(lambda car: car.demand('Play'), cars)

    def on_start_race(self):
        self.demand('Play')

    @staticmethod
    def exitPlay():
        LogMgr().log('exiting Play state')
        eng.show_cursor()

    def enterResults(self, race_ranking):
        self.mdt.gui.results.show(
            race_ranking, self.mdt.logic.player_car.lap_times,
            self.mdt.logic.drivers, self.mdt.logic.player_car.name)
        cars = [self.mdt.logic.player_car] + self.mdt.logic.cars
        map(lambda car: car.demand('Results'), cars)

    def exitResults(self):
        self.mdt.logic.exit_play()
        if self.shaders:
            eng.toggle_shader()
