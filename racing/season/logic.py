from yyagl.gameobject import LogicColleague
from yyagl.racing.ranking.ranking import Ranking
from yyagl.racing.tuning.tuning import Tuning
from yyagl.racing.race.race import RaceSinglePlayer, RaceServer, RaceClient


class SeasonLogic(LogicColleague):

    def __init__(self, mediator, season_props):
        LogicColleague.__init__(self, mediator)
        self.props = s_p = season_props
        self.ranking = Ranking(
            s_p.car_names, s_p.gameprops.menu_args.background_img, s_p.font,
            s_p.gameprops.menu_args.text_normal)
        self.tuning = Tuning(s_p)
        self.race = None
        self.drivers = s_p.drivers

    def start(self, reset=True):
        if reset:
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
        self.props.drivers = drivers

    def next_race(self):
        track = self.race.track.rprops.track_name
        ntracks = len(self.props.gameprops.season_tracks)
        if self.props.gameprops.season_tracks.index(track) == ntracks - 1:
            self.notify('on_season_end')
        else:
            idx = self.props.gameprops.season_tracks.index(track)
            next_track = self.props.gameprops.season_tracks[idx + 1]
            self.notify('on_season_cont', next_track,
                        self.props.player_car_name, self.props.drivers)

    def create_race_server(self, race_props):
        self.race = RaceServer(race_props)

    def create_race_client(self, race_props):
        self.race = RaceClient(race_props)

    def create_race(self, race_props):
        self.race = RaceSinglePlayer(race_props)

    def destroy(self):
        self.tuning.detach_obs(self.on_tuning_sel)
        self.props = self.ranking = self.tuning = self.race = None
        LogicColleague.destroy(self)
