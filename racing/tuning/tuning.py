from abc import ABCMeta
from yyagl.gameobject import GameObjectMdt
from .logic import TuningLogic
from .gui import TuningGui


class Tuning(GameObjectMdt):
    __metaclass__ = ABCMeta

    def __init__(self, cars, player_car, background, engine_img, tires_img,
                 suspensions_img):
        init_lst = [
            [('gui', TuningGui, [self, player_car, background, engine_img,
                                 tires_img, suspensions_img])],
            [('logic', TuningLogic, [self, cars])]]
        GameObjectMdt.__init__(self, init_lst)
