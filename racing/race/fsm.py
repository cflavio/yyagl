from yyagl.gameobject import Fsm
from yyagl.racing.race.gui.countdown import Countdown


class RaceFsm(Fsm):

    def __init__(self, mdt, shaders):
        self.countdown = None
        self.shaders = shaders
        Fsm.__init__(self, mdt)
        self.defaultTransitions = {
            'Loading': ['Countdown'],
            'Countdown': ['Play'],
            'Play': ['Results']}

    def enterLoading(self, track_path='', car_path='', player_cars=[],
                     drivers=None):
        eng.log_mgr.log('entering Loading state')  # facade
        args = [track_path, car_path, player_cars, drivers]
        self.mdt.gui.loading.enter_loading(*args)
        meth = self.mdt.logic.load_stuff
        taskMgr.doMethodLater(1.0, meth, 'loading', args[:-1])

    def exitLoading(self):
        eng.log_mgr.log('exiting Loading state')  # facade
        self.mdt.gui.loading.exit_loading()

    def enterCountdown(self):
        eng.gui.cursor.hide()  # facade
        self.countdown = Countdown()
        self.countdown.attach(self.on_start_race)
        self.mdt.logic.enter_play()
        if self.shaders:
            eng.shader_mgr.toggle_shader()  # facade
        cars = [game.player_car] + game.cars  #references into race
        map(lambda car: car.fsm.demand('Countdown'), cars)

    def exitCountdown(self):
        self.countdown.destroy()
        #eng.gfx.print_stats()

    @staticmethod
    def enterPlay():
        eng.log_mgr.log('entering Play state')  # facade
        map(lambda car: car.fsm.demand('Play'), [game.player_car] + game.cars)

    def on_start_race(self):
        self.demand('Play')

    @staticmethod
    def exitPlay():
        eng.log_mgr.log('exiting Play state')  # facade
        eng.gui.cursor.show()  # facade

    @staticmethod
    def enterResults(race_ranking):
        game.fsm.race.gui.results.show(race_ranking)
        cars = [game.player_car] + game.cars
        map(lambda car: car.fsm.demand('Results'), cars)

    def exitResults(self):
        self.mdt.logic.exit_play()
        if self.shaders:
            eng.shader_mgr.toggle_shader()  # facade
