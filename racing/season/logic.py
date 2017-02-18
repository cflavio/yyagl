from yyagl.gameobject import Logic
from yyagl.racing.ranking.ranking import Ranking
from yyagl.racing.tuning.tuning import Tuning


class SeasonLogic(Logic):

    def __init__(self, mdt):
        Logic.__init__(self, mdt)
        self.ranking = Ranking()
        self.tuning = Tuning()
        self.drivers = {}

    def start(self):
        self.ranking.logic.reset()
        self.tuning.logic.reset()
        self.drivers = {}

    def load(self):
        self.ranking.logic.load(game.options['save']['ranking'])
        self.tuning.logic.load(game.options['save']['tuning'])
        self.drivers = game.options['save']['drivers']

    @staticmethod
    def step():
        current_track = game.track.path[7:]
        tracks = ['prototype', 'desert']
        game.fsm.race.destroy()
        if tracks.index(current_track) == len(tracks) - 1:
            del game.options['save']
            game.options.store()
            game.fsm.demand('Menu')
        else:
            next_track = tracks[tracks.index(current_track) + 1]
            curr_car = game.options['save']['car']
            drivers = game.options['save']['drivers']
            n_t = 'tracks/' + next_track
            game.fsm.demand('Race', n_t, curr_car, [], drivers)


class SingleRaceSeasonLogic(SeasonLogic):

    @staticmethod
    def step():
        game.fsm.demand('Menu')
