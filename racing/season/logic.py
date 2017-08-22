from yyagl.gameobject import Logic
from yyagl.racing.ranking.ranking import Ranking
from yyagl.racing.tuning.tuning import Tuning
from yyagl.racing.race.race import RaceSinglePlayer, RaceServer, RaceClient


class SeasonLogic(Logic):

    def __init__(self, mdt, season_props):
        Logic.__init__(self, mdt)
        self.props = s_p = season_props
        self.ranking = Ranking(s_p.car_names, s_p.background_fpath, s_p.font,
                               s_p.fg_col)
        self.tuning = Tuning(s_p)
        self.race = None

    def start(self):
        self.ranking.reset()
        self.tuning.reset()
        self.tuning.attach_obs(self.on_tuning_sel)

    def on_tuning_sel(self, val):
        tun = self.tuning.car2tuning[self.props.player_car_name]
        setattr(tun, val, getattr(tun, val) + 1)
        self.next_race()

    def load(self, ranking, tuning, drivers):
        self.ranking.load(ranking)
        self.tuning.load(tuning)
        self.props._replace(drivers=drivers)

    def next_race(self):
        track = self.race.track.rprops.track_name
        ntracks = len(self.props.track_names)
        if self.props.track_names.index(track) == ntracks - 1:
            self.notify('on_season_end')
        else:
            idx = self.props.track_names.index(track)
            next_track = self.props.track_names[idx + 1]
            self.notify('on_season_cont', next_track,
                        self.props.player_car_name, self.props.drivers)

    def create_race_server(self, race_props):
        self.race = RaceServer(race_props)

    def create_race_client(self, race_props):
        self.race = RaceClient(race_props)

    def create_race(self, race_props, season_props):
        self.race = RaceSinglePlayer(race_props, season_props)

    def destroy(self):
        self.tuning.detach_obs(self.on_tuning_sel)
        self.props = self.ranking = self.tuning = self.race = None
        Logic.destroy(self)


class SingleRaceSeasonLogic(SeasonLogic):

    def next_race(self):
        game.demand('Menu')
