from yyagl.gameobject import GameObjectMdt
from .logic import SeasonLogic, SingleRaceSeasonLogic


class Season(GameObjectMdt):
    logic_cls = SeasonLogic

    def __init__(self, cars, player_car, skills, background, engine_img,
                 tires_img, suspensions_img, tracks, font):
        init_lst = [[('logic', self.logic_cls,
                      [self, cars, player_car, skills, background, engine_img,
                       tires_img, suspensions_img, tracks, font])]]
        GameObjectMdt.__init__(self, init_lst)


class SingleRaceSeason(Season):
    logic_cls = SingleRaceSeasonLogic
