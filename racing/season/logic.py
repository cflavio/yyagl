from yyagl.gameobject import Logic
from yyagl.racing.ranking.ranking import Ranking
from yyagl.racing.tuning.tuning import Tuning, TuningProps
from yyagl.racing.race.race import RaceSinglePlayer, RaceServer, RaceClient


class SeasonLogic(Logic):

    def __init__(self, mdt, season_props):
        Logic.__init__(self, mdt)
        self.props = s_p = season_props
        self.ranking = Ranking(s_p.cars, s_p.background, s_p.font, s_p.fg_col)
        tuning_props = TuningProps(
            s_p.cars, s_p.player_car, s_p.background, s_p.tuning_imgs)
        self.tuning = Tuning(tuning_props)
        self.drivers = s_p.drivers
        self.tracks = s_p.tracks
        self.player_car = s_p.player_car

    def start(self):
        self.ranking.logic.reset()
        self.tuning.logic.reset()
        self.tuning.attach_obs(self.on_tuning_done)

    def on_tuning_done(self):
        self.step()

    def load(self, ranking, tuning, drivers):
        self.ranking.load(ranking)
        self.tuning.load(tuning)
        self.drivers = drivers

    def step(self):
        track = game.track.props.path
        # todo: reference of race into season
        if self.props.tracks.index(track) == len(self.props.tracks) - 1:
            self.notify('on_season_end')
        else:
            next_track = self.props.tracks[self.props.tracks.index(track) + 1]
            self.notify('on_season_cont', next_track, self.props.player_car,
                        self.drivers)

    def create_race_server(self, keys, joystick, sounds):
        self.race = RaceServer(keys, joystick, sounds)

    def create_race_client(self, keys, joystick, sounds):
        self.race = RaceClient(keys, joystick, sounds)

    def create_race(self, race_props):
        self.race = RaceSinglePlayer(race_props)

    def destroy(self):
        self.tuning.detach_obs(self.on_tuning_done)
        Logic.destroy(self)


class SingleRaceSeasonLogic(SeasonLogic):

    def step(self):
        game.demand('Menu')
