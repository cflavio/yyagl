from yyagl.gameobject import GameObjectMdt
from .logic import SeasonLogic, SingleRaceSeasonLogic


class SeasonProps(object):

    def __init__(self, cars, player_car, skills, background, engine_img,
                 tires_img, suspensions_img, tracks, font, fg_col):
        self.cars = cars
        self.player_car = player_car
        self.skills = skills
        self.background = background
        self.engine_img = engine_img
        self.tires_img = tires_img
        self.suspensions_img = suspensions_img
        self.tracks = tracks
        self.font = font
        self.fg_col = fg_col


class Season(GameObjectMdt):
    logic_cls = SeasonLogic

    def __init__(self, season_props):
        init_lst = [[('logic', self.logic_cls, [self, season_props])]]
        GameObjectMdt.__init__(self, init_lst)


class SingleRaceSeason(Season):
    logic_cls = SingleRaceSeasonLogic
