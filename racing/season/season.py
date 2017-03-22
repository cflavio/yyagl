from yyagl.gameobject import GameObjectMdt
from .logic import SeasonLogic, SingleRaceSeasonLogic


class SeasonProps(object):

    def __init__(self, cars, player_car, drivers, background, tuning_imgs,
                 tracks, font, fg_col):
        self.cars = cars
        self.player_car = player_car
        self.drivers = drivers
        self.background = background
        self.tuning_imgs = tuning_imgs
        self.tracks = tracks
        self.font = font
        self.fg_col = fg_col


class SeasonFacade(object):

    def attach_obs(self, meth):
        return self.logic.attach(meth)

    def detach_obs(self, meth):
        return self.logic.detach(meth)

    @property
    def ranking(self):
        return self.logic.ranking

    @property
    def drivers(self):
        return self.logic.drivers

    @drivers.setter
    def drivers(self, val):
        self.logic.drivers = val


class Season(GameObjectMdt, SeasonFacade):
    logic_cls = SeasonLogic

    def __init__(self, season_props):
        init_lst = [[('logic', self.logic_cls, [self, season_props])]]
        GameObjectMdt.__init__(self, init_lst)


class SingleRaceSeason(Season):
    logic_cls = SingleRaceSeasonLogic
