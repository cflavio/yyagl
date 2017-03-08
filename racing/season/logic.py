from yyagl.gameobject import Logic
from yyagl.racing.ranking.ranking import Ranking
from yyagl.racing.tuning.tuning import Tuning


class SeasonLogic(Logic):

    def __init__(self, mdt, cars, player_car, skills, background, engine_img,
                 tires_img, suspensions_img, tracks, font):
        Logic.__init__(self, mdt)
        self.ranking = Ranking(cars, background, font)
        self.tuning = Tuning(cars, player_car, background, engine_img,
                             tires_img, suspensions_img)
        self.drivers = {}
        self.skills = skills
        self.tracks = tracks
        self.player_car = player_car

    def start(self):
        self.ranking.logic.reset()
        self.tuning.logic.reset()
        self.drivers = {}
        self.tuning.gui.attach(self.on_tuning_done)

    def on_tuning_done(self):
        self.step()

    def load(self, ranking, tuning, drivers):
        self.ranking.logic.load(ranking)
        self.tuning.logic.load(tuning)
        self.drivers = drivers

    def step(self):
        track = game.track.path[7:]
        # todo: reference of race into season
        if self.tracks.index(track) == len(self.tracks) - 1:
            self.notify('on_season_end')
        else:
            next_track = self.tracks[self.tracks.index(track) + 1]
            n_t = 'tracks/' + next_track
            self.notify('on_season_cont', n_t, self.player_car, self.drivers,
                        self.skills)

    def destroy(self):
        self.tuning.gui.detach(self.on_tuning_done)
        Logic.destroy(self)


class SingleRaceSeasonLogic(SeasonLogic):

    def step(self):
        game.fsm.demand('Menu')
