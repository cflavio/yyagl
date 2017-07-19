from yyagl.gameobject import Logic
from yyagl.racing.ranking.ranking import Ranking
from yyagl.racing.tuning.tuning import Tuning
from yyagl.racing.race.race import RaceSinglePlayer, RaceServer, RaceClient


class SeasonLogic(Logic):

    def __init__(self, mdt, season_props):
        Logic.__init__(self, mdt)
        self.props = s_p = season_props
        self.ranking = Ranking(s_p.cars, s_p.background_path, s_p.font, s_p.fg_col)
        self.tuning = Tuning(s_p)
        self.drivers = s_p.drivers
        self.tracks = s_p.tracks
        self.player_car = s_p.player_car
        self.race = None

    def start(self):
        self.ranking.logic.reset()
        self.tuning.logic.reset()
        self.tuning.attach_obs(self.on_tuning_sel)

    def on_tuning_sel(self, val):
        tun = self.tunings[self.props.player_car]
        setattr(tun, val, getattr(tun, val) + 1)
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
        self.tuning.detach_obs(self.on_tuning_sel)
        Logic.destroy(self)


class SingleRaceSeasonLogic(SeasonLogic):

    def step(self):
        game.demand('Menu')
