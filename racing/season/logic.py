from yyagl.gameobject import LogicColleague
from yyagl.racing.ranking.ranking import Ranking
from yyagl.racing.tuning.tuning import Tuning
from yyagl.racing.race.race import RaceSinglePlayer, RaceServer, RaceClient
from yyagl.racing.player.player import Player


class SeasonLogic(LogicColleague):

    def __init__(self, mediator, season_props):
        LogicColleague.__init__(self, mediator)
        self.props = s_p = season_props
        self.players = []
        car_names = [player.car for player in self.players]
        self.ranking = Ranking(
            car_names, s_p.gameprops.menu_props.background_img_path, s_p.font,
            s_p.gameprops.menu_props.text_normal_col)
        self.tuning = Tuning(s_p)
        self.race = None

    def start(self, reset=True):
        if reset:
            pass
            #self.ranking.reset()
            #self.tuning.reset()
        self.tuning.attach_obs(self.on_tuning_sel)

    def on_tuning_sel(self, val):
        #tun = self.tuning.car2tuning[self.props.player_car_name]
        tun = [player.tuning for player in self.players if player.kind == Player.human][0]
        setattr(tun, val, getattr(tun, val) + 1)
        #val2field = {'engine': 'tuning_engine', 'tires': 'tuning_tires',
        #             'suspensions': 'tuning_suspensions'}
        #field = val2field[val]
        #setattr(self.props, field, getattr(self.props, field) + 1)
        self.next_race()

    def load(self, ranking, tuning, drivers):
        self.ranking.load(ranking)
        self.tuning.load(tuning)
        self.props.drivers = drivers

    def next_race(self):
        track = self.race.track.race_props.track_name
        ntracks = len(self.props.gameprops.season_tracks)
        if self.props.gameprops.season_tracks.index(track) == ntracks - 1:
            self.notify('on_season_end')
        else:
            idx = self.props.gameprops.season_tracks.index(track)
            next_track = self.props.gameprops.season_tracks[idx + 1]
            self.notify('on_season_cont', next_track,
                        [player.car for player in self.players if player.kind == Player.human][0], self.players)

    def create_race_server(self, race_props, players):
        self.race = RaceServer(race_props, players)

    def create_race_client(self, race_props, players):
        self.race = RaceClient(race_props, players)

    def create_race(self, race_props, players):
        self.race = RaceSinglePlayer(race_props, players)

    def destroy(self):
        self.tuning.detach_obs(self.on_tuning_sel)
        self.props = self.ranking = self.tuning = self.race = None
        LogicColleague.destroy(self)
