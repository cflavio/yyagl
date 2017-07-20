from yyagl.gameobject import Logic
from yyagl.racing.ranking.ranking import Ranking
from yyagl.racing.tuning.tuning import Tuning
from yyagl.racing.race.race import RaceSinglePlayer, RaceServer, RaceClient


class SeasonLogic(Logic):

    def __init__(self, mdt, season_props):
        Logic.__init__(self, mdt)
        self.sprops = s_p = season_props
        self.ranking = Ranking(s_p.car_names, s_p.background_fpath, s_p.font, s_p.fg_col)
        self.tuning = Tuning(s_p)
        self.race = None

    def start(self):
        self.ranking.reset()
        self.tuning.reset()
        self.tuning.attach_obs(self.on_tuning_sel)

    def on_tuning_sel(self, val):
        tun = self.tuning.car2tuning[self.sprops.player_car_name]
        setattr(tun, val, getattr(tun, val) + 1)
        self.next_race()

    def load(self, ranking, tuning, drivers):
        self.ranking.load(ranking)
        self.tuning.load(tuning)
        self.sprops._replace(drivers=drivers)

    def next_race(self):
        track = self.race.track.rprops.track_name
        if self.sprops.track_names.index(track) == len(self.sprops.track_names) - 1:
            self.notify('on_season_end')
        else:
            next_track = self.sprops.track_names[self.sprops.track_names.index(track) + 1]
            self.notify('on_season_cont', next_track, self.sprops.player_car_name,
                        self.sprops.drivers)

    def create_race_server(self, keys, joystick, sounds):
        self.race = RaceServer(keys, joystick, sounds)

    def create_race_client(self, keys, joystick, sounds):
        self.race = RaceClient(keys, joystick, sounds)

    def create_race(self, race_props):
        self.race = RaceSinglePlayer(race_props)

    def destroy(self):
        self.tuning.detach_obs(self.on_tuning_sel)
        self.sprops = self.ranking = self.tuning = self.race = None
        Logic.destroy(self)


class SingleRaceSeasonLogic(SeasonLogic):

    def next_race(self):
        game.demand('Menu')
