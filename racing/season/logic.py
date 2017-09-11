from yyagl.gameobject import Logic
from yyagl.racing.ranking.ranking import Ranking
from yyagl.racing.tuning.tuning import Tuning
from yyagl.racing.tuning.logic import TuningCar
from yyagl.racing.race.race import RaceSinglePlayer, RaceServer, RaceClient
from yyagl.racing.driver.driver import Driver, DriverProps


class SeasonLogic(Logic):

    def __init__(self, mdt, season_props):
        Logic.__init__(self, mdt)
        self.props = s_p = season_props
        self.ranking = Ranking(s_p.car_names, s_p.gameprops.menu_args.background_img, s_p.font,
                               s_p.gameprops.menu_args.text_bg)
        self.tuning = Tuning(s_p)
        self.race = None

        self.drivers = s_p.drivers
        #self.drivers = []
        #for i, drv in enumerate(s_p.gameprops.drivers):
            #def get_driver(carname):
            #    for driver in drivers:
            #        if driver.car_name == carname:
            #            return driver
            #driver = get_driver(car_path)
            #carname2driver = {}
            #for driver in drivers:
            #driver_props = DriverProps(drv.car_id, drv.name, drv.speed, drv.adherence, drv.stability)
            #carname2driver[driver.car_name] = Driver(driver_props)
            #self.drivers += [Driver(driver_props)]

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
        self.props = self.props._replace(drivers=drivers)

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
        Logic.destroy(self)
