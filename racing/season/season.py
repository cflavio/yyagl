from collections import namedtuple
from yyagl.gameobject import GameObject
from .logic import SeasonLogic, SingleRaceSeasonLogic

sp_attrs = "car_names player_car_name drivers background_fpath tuning_imgs track_names " + \
    "font fg_col"
SeasonProps = namedtuple("SeasonProps", sp_attrs)


class SeasonFacade(object):

    def attach_obs(self, meth):
        return self.logic.attach(meth)

    def detach_obs(self, meth):
        return self.logic.detach(meth)

    def start(self):
        return self.logic.start()

    def load(self, ranking, tuning, drivers):
        return self.logic.load(ranking, tuning, drivers)

    @property
    def ranking(self):
        return self.logic.ranking

    @property
    def tuning(self):
        return self.logic.tuning

    @property
    def race(self):
        return self.logic.race

    @property
    def drivers(self):
        return self.logic.sprops.drivers

    @drivers.setter
    def drivers(self, val):
        self.logic.drivers = val

    def create_race_server(self, keys, joystick, sounds):
        return self.logic.create_race_server(keys, joystick, sounds)

    def create_race_client(self, keys, joystick, sounds):
        return self.logic.create_race_client(keys, joystick, sounds)

    def create_race(self, race_props):
        return self.logic.create_race(race_props)


class Season(GameObject, SeasonFacade):
    logic_cls = SeasonLogic

    def __init__(self, season_props):
        init_lst = [[('logic', self.logic_cls, [self, season_props])]]
        GameObject.__init__(self, init_lst)


class SingleRaceSeason(Season):
    logic_cls = SingleRaceSeasonLogic
