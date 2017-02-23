from yyagl.gameobject import Fsm
from yyagl.racing.race.gui.countdown import Countdown


class _Fsm(Fsm):

    def __init__(self, mdt):
        self.countdown = None
        Fsm.__init__(self, mdt)
        self.defaultTransitions = {
            'Loading': ['Countdown'],
            'Countdown': ['Play'],
            'Play': ['Results']}

    def enterLoading(self, track_path='', car_path='', player_cars=[],
                     drivers=None):
        eng.log_mgr.log('entering Loading state')
        args = [track_path, car_path, player_cars, drivers]
        self.mdt.gui.loading.enter_loading(*args)
        meth = self.mdt.logic.load_stuff
        taskMgr.doMethodLater(1.0, meth, 'loading', args[:-1])

    def exitLoading(self):
        eng.log_mgr.log('exiting Loading state')
        self.mdt.gui.loading.exit_loading()

    def enterCountdown(self):
        eng.gui.cursor.hide()
        self.countdown = Countdown()
        self.countdown.attach(self.on_start_race)
        self.mdt.logic.enter_play()
        if game.options['development']['shaders']:
            eng.shader_mgr.toggle_shader()
        cars = [game.player_car] + game.cars
        map(lambda car: car.fsm.demand('Countdown'), cars)

    def exitCountdown(self):
        self.countdown.destroy()
        #eng.gfx.print_stats()

    @staticmethod
    def enterPlay():
        eng.log_mgr.log('entering Play state')
        map(lambda car: car.fsm.demand('Play'), [game.player_car] + game.cars)

    def on_start_race(self):
        self.mdt.fsm.demand('Play')

    @staticmethod
    def exitPlay():
        eng.log_mgr.log('exiting Play state')
        eng.gui.cursor.show()

    @staticmethod
    def enterResults(race_ranking):
        game.fsm.race.gui.results.show(race_ranking)
        cars = [game.player_car] + game.cars
        map(lambda car: car.fsm.demand('Results'), cars)

    def exitResults(self):
        self.mdt.logic.exit_play()
        if game.options['development']['shaders']:
            eng.shader_mgr.toggle_shader()
